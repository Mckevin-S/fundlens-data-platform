"""Point d'entrée : `code-guard [fichiers...]`.

Sans argument, analyse tout le dépôt ; avec des fichiers (pre-commit), n'analyse que ceux-là.
Code de sortie 1 s'il reste au moins une erreur (les avertissements ne bloquent pas, sauf --strict).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from code_guard.config import Config
from code_guard.findings import Finding, Severity
from code_guard.rules import check_contracts, check_java_file, check_secrets, check_sql_files

TEXT_SUFFIXES = {".java", ".py", ".ts", ".js", ".sql", ".json", ".yml", ".yaml", ".toml", ".properties",
                 ".env", ".xml", ".cs", ".scala", ".md", ".sh", ".ps1", ".tf"}


def _iter_files(root: Path, config: Config, explicit: list[str]) -> list[Path]:
    if explicit:
        candidates = [(root / p).resolve() if not Path(p).is_absolute() else Path(p) for p in explicit]
    else:
        candidates = [p for p in root.rglob("*") if p.is_file()]
    return sorted(p for p in candidates
                  if p.is_file() and not config.is_excluded(p.relative_to(root))
                  and (p.suffix in TEXT_SUFFIXES or p.name.startswith(".env")))


def run(root: Path, files: list[str], config_path: Path | None = None) -> list[Finding]:
    root = root.resolve()
    config = Config.load(root, config_path)
    paths = _iter_files(root, config, files)
    findings: list[Finding] = []
    sql_roots = [(root / p).resolve() for p in config.sql_paths]
    sql_files = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        findings += check_secrets(path, text, config)
        if path.suffix == ".java":
            findings += check_java_file(path, text, config)
        if path.suffix == ".sql" and any(path.is_relative_to(r) for r in sql_roots):
            sql_files.append(path)
    findings += check_sql_files(sql_files, config)
    contracts_root = root / config.contracts_dir
    if not files or any(Path(f).resolve().is_relative_to(contracts_root.resolve()) for f in files):
        findings += check_contracts(config)
    return sorted(set(findings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="code-guard", description=__doc__)
    parser.add_argument("files", nargs="*", help="fichiers à analyser (par défaut : tout le dépôt)")
    parser.add_argument("--root", default=".", help="racine du dépôt")
    parser.add_argument("--config", help="chemin de code-guard.toml")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="les avertissements font aussi échouer")
    args = parser.parse_args(argv)

    findings = run(Path(args.root), args.files, Path(args.config) if args.config else None)
    errors = [f for f in findings if f.severity is Severity.ERROR]
    warnings = [f for f in findings if f.severity is Severity.WARNING]

    if args.format == "json":
        print(json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print(finding.format())
        print(f"code-guard : {len(errors)} erreur(s), {len(warnings)} avertissement(s)")
    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
