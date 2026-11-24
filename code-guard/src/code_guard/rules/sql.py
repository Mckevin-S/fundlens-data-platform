"""Lint SQL (modèles dbt) avec sqlfluff."""

from __future__ import annotations

from pathlib import Path

import sqlfluff

from code_guard.config import Config
from code_guard.findings import Finding, Severity


def check_sql_files(paths: list[Path], config: Config) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        sql = path.read_text(encoding="utf-8")
        rel = path.relative_to(config.root).as_posix()
        violations = sqlfluff.lint(sql, dialect=config.sql_dialect, exclude_rules=config.sql_exclude_rules or None)
        for violation in violations:
            code = violation.get("code", "")
            severity = Severity.WARNING if code.startswith(("LT", "CP")) else Severity.ERROR
            findings.append(Finding(rel, violation.get("start_line_no", 1), f"sql.{code}",
                                    violation.get("description", ""), severity))
    return findings
