"""Règles Java : nommage, injection par champ, sorties console, pureté du domaine hexagonal."""

from __future__ import annotations

import re
from pathlib import Path

from code_guard.config import Config
from code_guard.findings import Finding

TYPE_DECL = re.compile(r"^\s*(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+|sealed\s+|static\s+)*"
                       r"(class|interface|enum|record)\s+(\w+)")
PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;")
IMPORT = re.compile(r"^\s*import\s+(?:static\s+)?([\w.*]+)\s*;")
SYSOUT = re.compile(r"\bSystem\.(out|err)\.print")
AUTOWIRED = re.compile(r"^\s*@Autowired\b")
FIELD_DECL = re.compile(r"^\s*(?:private|protected|public)?\s*(?:final\s+)?[\w<>,.? \[\]]+\s+\w+\s*(=.*)?;\s*$")


def _is_main_source(path: Path) -> bool:
    return "src/main/java" in path.as_posix()


def check_java_file(path: Path, text: str, config: Config) -> list[Finding]:
    rel = path.relative_to(config.root).as_posix() if path.is_absolute() else path.as_posix()
    lines = text.splitlines()
    findings: list[Finding] = []
    package = ""
    public_type_seen = False

    for number, line in enumerate(lines, start=1):
        if match := PACKAGE.match(line):
            package = match.group(1)
        if match := TYPE_DECL.match(line):
            kind, name = match.groups()
            if not PASCAL_CASE.match(name):
                findings.append(Finding(rel, number, "java.naming", f"{kind} « {name} » doit être en PascalCase"))
            if line.lstrip().startswith("public") and not public_type_seen:
                public_type_seen = True
                if name != path.stem:
                    findings.append(Finding(rel, number, "java.naming",
                                            f"le type public « {name} » doit être dans {name}.java"))
        if _is_main_source(path) and SYSOUT.search(line):
            findings.append(Finding(rel, number, "java.no-sysout",
                                    "utiliser un logger (SLF4J) plutôt que System.out/err"))
        if AUTOWIRED.match(line):
            following = next((lines[i] for i in range(number, len(lines)) if lines[i].strip()), "")
            if FIELD_DECL.match(following) and "(" not in following:
                findings.append(Finding(rel, number, "java.no-field-injection",
                                        "injection par champ interdite : injecter par le constructeur"))

    domain_package = "." + package + "."
    if any(marker in domain_package for marker in config.domain_packages):
        for number, line in enumerate(lines, start=1):
            if (match := IMPORT.match(line)) and any(match.group(1).startswith(p)
                                                     for p in config.forbidden_in_domain):
                findings.append(Finding(rel, number, "java.domain-purity",
                                        f"le domaine ne doit pas dépendre de {match.group(1)}"))
    return findings
