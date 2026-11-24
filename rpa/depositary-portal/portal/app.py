"""Portail dépositaire simulé : pas d'API, seulement des pages web, comme beaucoup de portails réels.

Le robot UiPath s'y connecte, choisit la date et télécharge le relevé de positions en JSON.
"""

from __future__ import annotations

import json
import os
import secrets
from datetime import date

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

STATEMENTS = {
    ("FL-0001", "2026-11-20"): {"asOfDate": "2026-11-20", "fundId": "FL-0001", "sharesOutstanding": 125000,
                                "cash": 48250.75, "positions": [{"isin": "FR0000120271", "quantity": 12000},
                                                                {"isin": "FR0000131104", "quantity": 8500},
                                                                {"isin": "US0378331005", "quantity": 1500}]},
}

PAGE = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{title}</title></head>
<body><h1>{title}</h1>{body}</body></html>"""


def create_app(user: str | None = None, password: str | None = None) -> FastAPI:
    user = user or os.environ.get("PORTAL_USER", "robot")
    password = password or os.environ.get("PORTAL_PASSWORD", "demo-only")
    sessions: set[str] = set()
    app = FastAPI(title="Portail dépositaire (simulé)")

    def require_session(request: Request) -> None:
        if request.cookies.get("session") not in sessions:
            raise HTTPException(status_code=401, detail="Session expirée")

    @app.get("/", response_class=HTMLResponse)
    def login_page() -> str:
        form = ('<form method="post" action="/login"><label>Identifiant <input id="user" name="user"></label>'
                '<label>Mot de passe <input id="password" name="password" type="password"></label>'
                '<button id="submit" type="submit">Connexion</button></form>')
        return PAGE.format(title="Connexion dépositaire", body=form)

    @app.post("/login")
    def login(user_in: str = Form(alias="user"), password_in: str = Form(alias="password")):
        if not (secrets.compare_digest(user_in, user) and secrets.compare_digest(password_in, password)):
            error = '<p id="error">Identifiants invalides</p>'
            return HTMLResponse(PAGE.format(title="Connexion dépositaire", body=error), status_code=401)
        token = secrets.token_urlsafe(16)
        sessions.add(token)
        response = RedirectResponse("/statements", status_code=303)
        response.set_cookie("session", token, httponly=True, samesite="strict")
        return response

    @app.get("/statements", response_class=HTMLResponse)
    def statements(request: Request) -> str:
        require_session(request)
        rows = "".join(f'<tr><td>{f}</td><td>{d}</td><td><a class="download" href="/statements/{f}/{d}.json">'
                       f"Télécharger</a></td></tr>" for f, d in sorted(STATEMENTS))
        return PAGE.format(title="Relevés de positions",
                           body=f'<table id="statements"><tr><th>Fonds</th><th>Date</th><th></th></tr>{rows}</table>')

    @app.get("/statements/{fund_id}/{day}.json")
    def download(fund_id: str, day: str, request: Request) -> JSONResponse:
        require_session(request)
        date.fromisoformat(day)
        statement = STATEMENTS.get((fund_id, day))
        if statement is None:
            raise HTTPException(status_code=404, detail="Relevé introuvable")
        return JSONResponse(json.loads(json.dumps(statement)),
                            headers={"Content-Disposition": f'attachment; filename="positions-{fund_id}-{day}.json"'})

    return app
