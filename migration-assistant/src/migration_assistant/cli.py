"""migration-assistant migrate <sources> --out <dossier> [--llm]
   migration-assistant tests <fichier> --framework junit5|jasmine --out <fichier>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from migration_assistant.converter import classify, convert_resource, convert_service
from migration_assistant.llm import REVIEW_HEADER, OllamaClient, leftovers_prompt, strip_fences, tests_prompt


def migrate(sources: Path, out: Path, client: OllamaClient | None = None) -> dict:
    report = {"converted": [], "copied": [], "skipped": [], "leftovers": {}}
    for path in sorted(sources.rglob("*.java")):
        rel = path.relative_to(sources)
        java = path.read_text(encoding="utf-8")
        kind = classify(java)
        if kind == "jaxrs-application":
            report["skipped"].append(str(rel))
            continue
        if kind == "resource":
            result = convert_resource(java)
            rel = rel.with_name(rel.name.replace("Resource.java", "Controller.java"))
        elif kind == "ejb":
            result = convert_service(java)
        else:
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(java.replace("javax.persistence", "jakarta.persistence"), encoding="utf-8")
            report["copied"].append(str(rel))
            continue
        source = result.source
        if result.leftovers:
            report["leftovers"][str(rel)] = result.leftovers
            if client is not None:
                proposal = strip_fences(client.generate(leftovers_prompt(str(rel), source, result.leftovers)))
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                (out / rel).with_suffix(".llm.java.txt").write_text(f"{REVIEW_HEADER}\n{proposal}", encoding="utf-8")
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        report["converted"].append(str(rel))
    return report


def generate_tests(source_file: Path, framework: str, out: Path, client: OllamaClient) -> Path:
    code = strip_fences(client.generate(tests_prompt(source_file.stem, source_file.read_text(encoding="utf-8"), framework)))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"{REVIEW_HEADER}\n{code}", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="migration-assistant", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    m = sub.add_parser("migrate", help="convertir un dossier de sources Jakarta EE")
    m.add_argument("sources", type=Path)
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--llm", action="store_true", help="demander au LLM local une proposition pour le reste à faire")
    t = sub.add_parser("tests", help="générer des tests avec le LLM local (à relire)")
    t.add_argument("source", type=Path)
    t.add_argument("--framework", choices=["junit5", "jasmine"], default="junit5")
    t.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "migrate":
        report = migrate(args.sources, args.out, OllamaClient() if args.llm else None)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    path = generate_tests(args.source, "JUnit 5 + AssertJ" if args.framework == "junit5" else "Jasmine", args.out,
                          OllamaClient())
    print(f"Tests générés dans {path} – à relire avant commit")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
