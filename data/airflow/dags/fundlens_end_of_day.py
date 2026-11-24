"""DAG de fin de journée : relevés dépositaire (robot UiPath), fichiers de marché, back-office Oracle
→ validation des contrats → HDFS (zone brute) + archive S3 → BigQuery → dbt → calcul Spark."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

INBOX = Path("/opt/fundlens/inbox")


@dag(
    dag_id="fundlens_end_of_day",
    schedule="30 19 * * 1-5",
    start_date=datetime(2026, 11, 2),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["fundlens", "ingestion"],
)
def fundlens_end_of_day():
    @task
    def validate_market_prices(ds: str | None = None) -> dict:
        from fundlens_ingestion.tasks import validate

        return validate(json.loads((INBOX / f"market-prices-{ds}.json").read_text()), "market-prices")

    @task
    def validate_positions(ds: str | None = None) -> list[dict]:
        from fundlens_ingestion.tasks import validate

        return [validate(json.loads(p.read_text()), "positions") for p in sorted(INBOX.glob(f"positions-*-{ds}.json"))]

    @task
    def extract_backoffice(ds: str | None = None) -> list[dict]:
        from datetime import date

        from airflow.providers.oracle.hooks.oracle import OracleHook
        from fundlens_ingestion.tasks import extract_operations

        with OracleHook(oracle_conn_id="oracle_backoffice").get_conn() as conn:
            return extract_operations(conn.cursor(), date.fromisoformat(ds))

    @task
    def land_raw(prices: dict, snapshots: list[dict], operations: list[dict], ds: str | None = None) -> None:
        from datetime import date

        import boto3
        import requests
        from airflow.models import Variable
        from fundlens_ingestion.tasks import HdfsWriter, archive_to_s3, fx_to_csv, positions_to_csv, raw_path

        day = date.fromisoformat(ds)
        hdfs = HdfsWriter(Variable.get("webhdfs_url"), "fundlens", requests.Session())
        s3 = boto3.client("s3")
        bucket = Variable.get("raw_archive_bucket")
        files = {raw_path("market-prices", day, "prices.json"): json.dumps(prices).encode(),
                 raw_path("fx", day, "fx.csv"): fx_to_csv(prices).encode(),
                 raw_path("operations", day, "operations.json"): json.dumps(operations, default=str).encode()}
        for snap in snapshots:
            files[raw_path("positions", day, f"{snap['fundId']}.csv")] = positions_to_csv(snap).encode()
        for path, data in files.items():
            hdfs.write(path, data)
            archive_to_s3(s3, bucket, path.lstrip("/"), data)

    @task
    def load_warehouse(prices: dict) -> int:
        from airflow.models import Variable
        from fundlens_ingestion.tasks import load_to_bigquery
        from google.cloud import bigquery

        rows = [{"as_of": prices["asOfDate"], **p} for p in prices["prices"]]
        return load_to_bigquery(bigquery.Client(), Variable.get("bq_raw_prices_table"), rows)

    prices, snapshots, operations = validate_market_prices(), validate_positions(), extract_backoffice()
    landed = land_raw(prices, snapshots, operations)
    loaded = load_warehouse(prices)

    valuation = SparkSubmitOperator(
        task_id="spark_valuation",
        application="/opt/fundlens/jobs/fundlens-spark-assembly.jar",
        java_class="com.fundlens.spark.ValuationJob",
        application_args=["--date", "{{ ds }}"],
        conn_id="spark_yarn",
    )
    dbt_build = BashOperator(task_id="dbt_build", bash_command="cd /opt/fundlens/dbt && dbt build --target bigquery")

    landed >> valuation
    [landed, loaded] >> dbt_build


fundlens_end_of_day()
