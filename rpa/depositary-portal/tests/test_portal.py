import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from portal.app import create_app


def client():
    return TestClient(create_app("robot", "s3cret-test"))


def test_parcours_du_robot_connexion_liste_et_telechargement():
    c = client()
    assert 'id="user"' in c.get("/").text
    page = c.post("/login", data={"user": "robot", "password": "s3cret-test"})
    assert page.status_code == 200 and 'id="statements"' in page.text
    statement = c.get("/statements/FL-0001/2026-11-20.json")
    assert statement.headers["content-disposition"].endswith('positions-FL-0001-2026-11-20.json"')
    assert statement.json()["fundId"] == "FL-0001"


def test_identifiants_invalides_et_acces_sans_session():
    c = client()
    assert c.post("/login", data={"user": "robot", "password": "faux"}).status_code == 401
    assert c.get("/statements").status_code == 401


def test_releve_inconnu():
    c = client()
    c.post("/login", data={"user": "robot", "password": "s3cret-test"})
    assert c.get("/statements/FL-0002/2026-11-20.json").status_code == 404
