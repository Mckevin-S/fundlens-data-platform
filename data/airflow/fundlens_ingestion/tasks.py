from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator

CONTRACTS = Path(__file__).resolve().parents[3] / "contracts"


class InvalidFileError(ValueError):
    """Le fichier reçu ne respecte pas son contrat : il est rejeté et mis en quarantaine."""


def validate(document: dict, contract: str, contracts_dir: Path = CONTRACTS) -> dict:
    schema = json.loads((contracts_dir / f"{contract}.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(f"{'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in errors[:5])
        raise InvalidFileError(f"{contract} invalide ({len(errors)} erreur(s)) : {details}")
    return document


def extract_operations(cursor: Any, as_of: date) -> list[dict]:
    """ELT : extraction brute des opérations du back-office Oracle pour la journée (transformations dans dbt)."""
    cursor.execute(
        "SELECT ID, FUND_ID, TRADE_DATE, OP_TYPE, ISIN, QUANTITY, AMOUNT FROM OPERATIONS "
        "WHERE TRADE_DATE = :as_of ORDER BY ID",
        as_of=as_of,
    )
    columns = [c[0].lower() for c in cursor.description]
    return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def positions_to_csv(snapshot: dict) -> str:
    """Contrat Positions (JSON) → lignes CSV au format de la table brute positions."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["as_of", "fund_id", "shares_outstanding", "cash", "isin", "quantity"])
    for line in snapshot["positions"]:
        writer.writerow([snapshot["asOfDate"], snapshot["fundId"], snapshot["sharesOutstanding"], snapshot["cash"],
                         line["isin"], line["quantity"]])
    return out.getvalue()


class HttpSession(Protocol):
    def put(self, url: str, **kwargs: Any) -> Any: ...


@dataclass
class HdfsWriter:
    """Écriture via l'API WebHDFS (deux étapes : redirection vers un datanode puis envoi)."""

    base_url: str
    user: str
    session: HttpSession

    def write(self, path: str, data: bytes) -> str:
        url = f"{self.base_url}/webhdfs/v1{path}?op=CREATE&overwrite=true&user.name={self.user}"
        first = self.session.put(url, allow_redirects=False)
        location = first.headers.get("Location")
        if first.status_code != 307 or not location:
            raise RuntimeError(f"WebHDFS : redirection attendue, reçu {first.status_code}")
        second = self.session.put(location, data=data)
        if second.status_code != 201:
            raise RuntimeError(f"WebHDFS : écriture refusée ({second.status_code})")
        return path


def fx_to_csv(prices: dict) -> str:
    rows = [f"{prices['asOfDate']},{fx['currency']},{fx['rateToEur']}" for fx in prices.get("fxRates", [])]
    return "\n".join(["as_of,currency,rate_to_eur", *rows]) + "\n"


def raw_path(kind: str, as_of: date, name: str) -> str:
    return f"/fundlens/raw/{kind}/as_of={as_of.isoformat()}/{name}"


def archive_to_s3(s3_client: Any, bucket: str, key: str, data: bytes) -> str:
    s3_client.put_object(Bucket=bucket, Key=key, Body=data, ServerSideEncryption="AES256")
    return f"s3://{bucket}/{key}"


def load_to_bigquery(bq_client: Any, table: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    errors = bq_client.insert_rows_json(table, rows)
    if errors:
        raise RuntimeError(f"BigQuery : {len(errors)} ligne(s) rejetée(s)")
    return len(rows)
