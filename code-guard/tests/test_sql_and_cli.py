import json

from code_guard.cli import main, run
from code_guard.config import Config

CONFIG = """
[code-guard]
excludes = [".git", "target"]
[code-guard.sql]
dialect = "bigquery"
paths = ["data/dbt"]
[code-guard.contracts]
dir = "contracts"
[code-guard.java]
domain_packages = [".domain."]
"""


def test_config_defaults_when_file_missing(repo):
    cfg = Config.load(repo.root)
    assert cfg.sql_dialect == "bigquery" and cfg.contracts_dir == "contracts"


def test_config_is_read_from_toml(repo):
    repo("code-guard.toml", CONFIG.replace('"bigquery"', '"snowflake"'))
    assert Config.load(repo.root).sql_dialect == "snowflake"


def test_clean_sql_passes_and_bad_sql_is_reported(repo):
    repo("code-guard.toml", CONFIG)
    repo("data/dbt/models/ok.sql", "select\n    fund_id,\n    nav\nfrom navs\n")
    repo("data/dbt/models/bad.sql", "SELECT fund_id,nav FROM navs WHERE\n")
    findings = run(repo.root, [])
    assert findings and all(f.path == "data/dbt/models/bad.sql" for f in findings)


def test_sql_outside_configured_paths_is_ignored(repo):
    repo("code-guard.toml", CONFIG)
    repo("scripts/adhoc.sql", "SELECT a,b FROM t WHERE\n")
    assert run(repo.root, []) == []


def test_cli_exit_codes_and_json_output(repo, capsys):
    repo("code-guard.toml", CONFIG)
    repo("svc/src/main/java/a/Demo.java", "package a;\npublic class Demo { void x(){ System.out.println(1);} }\n")
    assert main(["--root", str(repo.root), "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["rule"] == "java.no-sysout" and payload[0]["severity"] == "error"


def test_cli_only_checks_given_files(repo, capsys):
    repo("code-guard.toml", CONFIG)
    repo("svc/src/main/java/a/Demo.java", "package a;\npublic class Demo { void x(){ System.out.println(1);} }\n")
    ok = repo("svc/src/main/java/a/Ok.java", "package a;\npublic class Ok {}\n")
    assert main(["--root", str(repo.root), str(ok)]) == 0
    assert "0 erreur(s)" in capsys.readouterr().out


def test_warnings_only_fail_in_strict_mode(repo):
    repo("code-guard.toml", CONFIG)
    repo("data/dbt/models/style.sql", "SELECT a from t\n")
    assert main(["--root", str(repo.root)]) == 0
    assert main(["--root", str(repo.root), "--strict"]) == 1


def test_excluded_directories_are_skipped(repo):
    repo("code-guard.toml", CONFIG)
    repo("target/Gen.java", "public class wrong {}")
    assert run(repo.root, []) == []
