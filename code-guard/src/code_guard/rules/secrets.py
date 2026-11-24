"""Détection de secrets commités par erreur."""

from __future__ import annotations

import re
from pathlib import Path

from code_guard.config import Config
from code_guard.findings import Finding

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("clé d'accès AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("clé privée", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("jeton GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("mot de passe en clair", re.compile(
        r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*[\"'](?!\$\{)[^\"'\s]{8,}[\"']")),
]


def check_secrets(path: Path, text: str, config: Config) -> list[Finding]:
    if path.name in config.secret_allowlist:
        return []
    rel = path.relative_to(config.root).as_posix() if path.is_absolute() else path.as_posix()
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        for label, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(rel, number, "secrets.detected", f"{label} probable : à retirer du dépôt"))
    return findings
