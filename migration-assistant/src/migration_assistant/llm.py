"""Appel facultatif à un LLM local (Ollama) : propositions pour le reste à faire et génération de tests.

Aucune clé d'API : le modèle tourne en local. Toute sortie du LLM est marquée « À RELIRE ».
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable

REVIEW_HEADER = "// GÉNÉRÉ PAR IA – À RELIRE AVANT COMMIT"

Transport = Callable[[str, dict], dict]


def _http_post(url: str, payload: dict) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, transport: Transport = _http_post):
        self.base_url = (base_url or os.environ.get("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
        self.transport = transport

    def generate(self, prompt: str) -> str:
        answer = self.transport(f"{self.base_url}/api/generate",
                                {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0}})
        return answer.get("response", "").strip()


def leftovers_prompt(file_name: str, source: str, leftovers: list[str]) -> str:
    items = "\n".join(f"- {item}" for item in leftovers)
    return (f"Tu migres une application Jakarta EE vers Spring Boot 3.3 (Java 21).\n"
            f"Fichier : {file_name}\nPoints non convertis automatiquement :\n{items}\n\n"
            f"Code actuel :\n```java\n{source}\n```\n"
            "Propose uniquement le code Java corrigé, sans explication.")


def tests_prompt(class_name: str, source: str, framework: str) -> str:
    return (f"Écris des tests {framework} pour la classe {class_name} ci-dessous. "
            "Couvre le cas nominal, les cas limites et les erreurs. Réponds uniquement avec le code du test.\n"
            f"```\n{source}\n```")


def strip_fences(text: str) -> str:
    lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
    return "\n".join(lines).strip() + "\n"
