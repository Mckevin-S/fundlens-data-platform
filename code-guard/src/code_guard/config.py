from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_EXCLUDES = (".git", "node_modules", "target", "build", "dist", ".venv", "__pycache__")


@dataclass
class Config:
    """Configuration lue dans code-guard.toml (section [code-guard])."""

    root: Path
    sql_dialect: str = "bigquery"
    sql_paths: list[str] = field(default_factory=lambda: ["data/dbt"])
    sql_exclude_rules: list[str] = field(default_factory=list)
    contracts_dir: str = "contracts"
    domain_packages: list[str] = field(default_factory=lambda: [".domain."])
    forbidden_in_domain: list[str] = field(
        default_factory=lambda: ["org.springframework", "jakarta.persistence", "javax.persistence"]
    )
    excludes: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDES))
    secret_allowlist: list[str] = field(default_factory=lambda: [".env.example"])

    @classmethod
    def load(cls, root: Path, path: Path | None = None) -> Config:
        path = path or root / "code-guard.toml"
        if not path.exists():
            return cls(root=root)
        with path.open("rb") as fh:
            data = tomllib.load(fh).get("code-guard", {})
        sql = data.get("sql", {})
        java = data.get("java", {})
        secrets = data.get("secrets", {})
        cfg = cls(root=root)
        cfg.sql_dialect = sql.get("dialect", cfg.sql_dialect)
        cfg.sql_paths = sql.get("paths", cfg.sql_paths)
        cfg.sql_exclude_rules = sql.get("exclude_rules", cfg.sql_exclude_rules)
        cfg.contracts_dir = data.get("contracts", {}).get("dir", cfg.contracts_dir)
        cfg.domain_packages = java.get("domain_packages", cfg.domain_packages)
        cfg.forbidden_in_domain = java.get("forbidden_in_domain", cfg.forbidden_in_domain)
        cfg.excludes = data.get("excludes", cfg.excludes)
        cfg.secret_allowlist = secrets.get("allowlist", cfg.secret_allowlist)
        return cfg

    def is_excluded(self, path: Path) -> bool:
        return any(part in self.excludes for part in path.parts)
