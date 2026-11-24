"""Contrats JSON des data products : schémas valides et exemples conformes.

Organisation attendue :
  contracts/<nom>.schema.json            schéma JSON (draft 2020-12)
  contracts/examples/<nom>/*.json        exemples qui doivent respecter le schéma
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from code_guard.config import Config
from code_guard.findings import Finding


def _rel(path: Path, config: Config) -> str:
    return path.relative_to(config.root).as_posix()


def _load(path: Path, config: Config, findings: list[Finding]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        findings.append(Finding(_rel(path, config), exc.lineno, "contracts.json", f"JSON invalide : {exc.msg}"))
        return None


def check_contracts(config: Config) -> list[Finding]:
    base = config.root / config.contracts_dir
    findings: list[Finding] = []
    if not base.is_dir():
        return findings
    for schema_path in sorted(base.glob("*.schema.json")):
        schema = _load(schema_path, config, findings)
        if schema is None:
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            findings.append(Finding(_rel(schema_path, config), 1, "contracts.schema", f"schéma invalide : {exc.message}"))
            continue
        if "$id" not in schema or "version" not in schema:
            findings.append(Finding(_rel(schema_path, config), 1, "contracts.metadata",
                                    "un contrat doit déclarer « $id » et « version »"))
        name = schema_path.name.removesuffix(".schema.json")
        examples = sorted((base / "examples" / name).glob("*.json"))
        if not examples:
            findings.append(Finding(_rel(schema_path, config), 1, "contracts.examples",
                                    f"aucun exemple dans {config.contracts_dir}/examples/{name}/"))
        validator = Draft202012Validator(schema)
        for example_path in examples:
            document = _load(example_path, config, findings)
            if document is None:
                continue
            for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
                where = "/".join(str(p) for p in error.path) or "(racine)"
                findings.append(Finding(_rel(example_path, config), 1, "contracts.example",
                                        f"{where} : {error.message}"))
    return findings
