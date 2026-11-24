import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fundlens_ingestion.tasks import (
    HdfsWriter,
    InvalidFileError,
    archive_to_s3,
    extract_operations,
    fx_to_csv,
    load_to_bigquery,
    positions_to_csv,
    raw_path,
    validate,
)

EXAMPLES = Path(__file__).resolve().parents[3] / "contracts/examples"


def example(name):
    return json.loads(next((EXAMPLES / name).glob("*.json")).read_text())


def test_les_exemples_respectent_leurs_contrats():
    assert validate(example("market-prices"), "market-prices")["source"] == "simulateur-marche"
    assert validate(example("positions"), "positions")["fundId"] == "FL-0001"


def test_un_fichier_invalide_est_rejete_avec_le_detail():
    bad = example("market-prices")
    bad["prices"][0]["close"] = -3
    with pytest.raises(InvalidFileError, match="prices/0/close"):
        validate(bad, "market-prices")


def test_positions_vers_csv_identique_au_seed_dbt():
    csv_text = positions_to_csv(example("positions"))
    seed = (Path(__file__).resolve().parents[2] / "dbt/seeds/positions.csv").read_text().splitlines()
    assert csv_text.splitlines() == seed[:4]


class FakeCursor:
    description = (("ID",), ("FUND_ID",), ("AMOUNT",))

    def __init__(self):
        self.executed = None

    def execute(self, sql, **params):
        self.executed = (sql, params)

    def fetchall(self):
        return [(1, "FL-0001", 6142.0)]


def test_extraction_oracle_parametree():
    cursor = FakeCursor()
    rows = extract_operations(cursor, date(2026, 11, 20))
    assert rows == [{"id": 1, "fund_id": "FL-0001", "amount": 6142.0}]
    assert ":as_of" in cursor.executed[0] and cursor.executed[1] == {"as_of": date(2026, 11, 20)}


class Resp:
    def __init__(self, status, headers=None):
        self.status_code, self.headers = status, headers or {}


class FakeSession:
    def __init__(self, responses):
        self.responses, self.calls = list(responses), []

    def put(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def test_webhdfs_en_deux_etapes():
    session = FakeSession([Resp(307, {"Location": "http://dn1:9864/write"}), Resp(201)])
    path = raw_path("positions", date(2026, 11, 20), "FL-0001.csv")
    HdfsWriter("http://nn:9870", "fundlens", session).write(path, b"x")
    assert session.calls[0][0] == ("http://nn:9870/webhdfs/v1/fundlens/raw/positions/as_of=2026-11-20/FL-0001.csv"
                                   "?op=CREATE&overwrite=true&user.name=fundlens")
    assert session.calls[1] == ("http://dn1:9864/write", {"data": b"x"})


@pytest.mark.parametrize("responses", [[Resp(200)], [Resp(307, {"Location": "u"}), Resp(403)]])
def test_webhdfs_erreurs(responses):
    with pytest.raises(RuntimeError):
        HdfsWriter("http://nn", "u", FakeSession(responses)).write("/p", b"x")


def test_archive_s3_chiffree_et_chargement_bigquery():
    class S3:
        def put_object(self, **kw):
            self.kw = kw

    class BQ:
        def __init__(self, errors):
            self.errors = errors

        def insert_rows_json(self, table, rows):
            return self.errors

    s3 = S3()
    assert archive_to_s3(s3, "raw", "a/b.json", b"{}") == "s3://raw/a/b.json"
    assert s3.kw["ServerSideEncryption"] == "AES256"
    assert load_to_bigquery(BQ([]), "p.d.t", [{"a": 1}]) == 1
    assert load_to_bigquery(BQ([]), "p.d.t", []) == 0
    with pytest.raises(RuntimeError):
        load_to_bigquery(BQ([{"err": 1}]), "p.d.t", [{"a": 1}])


def test_taux_de_change_vers_csv():
    assert fx_to_csv(example("market-prices")) == "as_of,currency,rate_to_eur\n2026-11-20,USD,0.92\n"
