from code_guard.config import Config
from code_guard.rules.contracts import check_contracts

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://fundlens.local/contracts/prices.schema.json",
    "version": "1.0.0",
    "type": "object",
    "required": ["isin", "price"],
    "properties": {"isin": {"type": "string", "pattern": "^[A-Z]{2}[A-Z0-9]{9}[0-9]$"},
                   "price": {"type": "number", "exclusiveMinimum": 0}},
}


def rules(repo):
    return sorted(f.rule for f in check_contracts(Config(root=repo.root)))


def test_valid_contract_with_valid_example(repo):
    repo("contracts/prices.schema.json", SCHEMA)
    repo("contracts/examples/prices/ok.json", {"isin": "FR0010315770", "price": 12.5})
    assert rules(repo) == []


def test_example_violating_contract_is_reported(repo):
    repo("contracts/prices.schema.json", SCHEMA)
    repo("contracts/examples/prices/bad.json", {"isin": "nope", "price": -1})
    findings = check_contracts(Config(root=repo.root))
    assert [f.rule for f in findings] == ["contracts.example", "contracts.example"]
    assert "isin" in findings[0].message


def test_missing_metadata_and_examples(repo):
    schema = dict(SCHEMA)
    del schema["version"]
    repo("contracts/prices.schema.json", schema)
    assert rules(repo) == ["contracts.examples", "contracts.metadata"]


def test_invalid_schema_and_invalid_json(repo):
    repo("contracts/broken.schema.json", {"type": 42})
    repo("contracts/notjson.schema.json", "{ not json")
    assert rules(repo) == ["contracts.json", "contracts.schema"]


def test_invalid_json_example(repo):
    repo("contracts/prices.schema.json", SCHEMA)
    repo("contracts/examples/prices/broken.json", "{")
    assert rules(repo) == ["contracts.json"]


def test_no_contracts_dir_is_fine(repo):
    assert rules(repo) == []
