"""Structure du DAG (exécuté en CI, où Airflow est installé)."""

import pytest

airflow = pytest.importorskip("airflow")


def test_dag_charge_sans_erreur():
    from airflow.models import DagBag

    bag = DagBag(dag_folder="data/airflow/dags", include_examples=False)
    assert bag.import_errors == {}
    dag = bag.get_dag("fundlens_end_of_day")
    assert {"validate_market_prices", "land_raw", "spark_valuation", "dbt_build"} <= set(dag.task_ids)
    assert dag.get_task("dbt_build").upstream_task_ids == {"land_raw", "load_warehouse"}
