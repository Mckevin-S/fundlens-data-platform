from code_guard.cli import run

CONFIG = '[code-guard]\n[code-guard.sql]\ndialect = "bigquery"\npaths = ["data/dbt"]\n'
LONG = "select\n    a_very_long_column_name_number_one, a_very_long_column_name_number_two, col_three\nfrom t\n"


def test_root_sqlfluff_file_is_used(repo):
    repo("code-guard.toml", CONFIG)
    repo("data/dbt/models/m.sql", LONG)
    assert any(f.rule == "sql.LT05" for f in run(repo.root, []))
    repo(".sqlfluff", "[sqlfluff]\nmax_line_length = 200\n")
    assert not any(f.rule == "sql.LT05" for f in run(repo.root, []))
