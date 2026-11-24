import json
from pathlib import Path

from migration_assistant.cli import generate_tests, main, migrate
from migration_assistant.llm import REVIEW_HEADER, OllamaClient, leftovers_prompt, strip_fences

LEGACY = Path(__file__).resolve().parents[2] / "legacy-backoffice/src/main/java"


class FakeTransport:
    def __init__(self, answer: str):
        self.answer = answer
        self.calls = []

    def __call__(self, url, payload):
        self.calls.append((url, payload))
        return {"response": self.answer}


def test_migrate_the_legacy_backoffice(tmp_path):
    report = migrate(LEGACY, tmp_path)
    base = "com/fundlens/legacy/"
    assert report["converted"] == [base + "OperationController.java", base + "OperationService.java"]
    assert report["copied"] == [base + "Operation.java", base + "OperationValidator.java"]
    assert report["skipped"] == [base + "JaxRsApplication.java"]
    assert (tmp_path / base / "OperationController.java").exists()


def test_llm_proposal_is_written_for_leftovers(tmp_path):
    src = tmp_path / "src/a"
    src.mkdir(parents=True)
    (src / "Batch.java").write_text('package a;\nimport jakarta.ejb.Singleton;\n@Singleton\npublic class Batch {\n'
                                    '  @Schedule(hour="2") public void run() {}\n}\n')
    fake = FakeTransport("```java\n@Scheduled(cron = \"0 0 2 * * *\")\n```")
    out = tmp_path / "out"
    report = migrate(tmp_path / "src", out, OllamaClient("http://ollama:11434", "test", fake))
    assert "a/Batch.java" in report["leftovers"]
    proposal = (out / "a/Batch.llm.java.txt").read_text()
    assert proposal.startswith(REVIEW_HEADER) and "@Scheduled" in proposal and "```" not in proposal
    assert fake.calls[0][0] == "http://ollama:11434/api/generate"
    assert fake.calls[0][1]["options"]["temperature"] == 0


def test_generate_tests_marks_output_for_review(tmp_path):
    fake = FakeTransport("```java\nclass OperationValidatorTest {}\n```")
    out = generate_tests(LEGACY / "com/fundlens/legacy/OperationValidator.java", "JUnit 5", tmp_path / "T.java",
                         OllamaClient(transport=fake))
    assert out.read_text() == f"{REVIEW_HEADER}\nclass OperationValidatorTest {{}}\n"
    assert "OperationValidator" in fake.calls[0][1]["prompt"]


def test_cli_migrate_prints_json_report(tmp_path, capsys):
    assert main(["migrate", str(LEGACY), "--out", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out)["skipped"]


def test_cli_tests_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("migration_assistant.cli.OllamaClient", lambda: OllamaClient(transport=FakeTransport("x")))
    assert main(["tests", str(LEGACY / "com/fundlens/legacy/Operation.java"), "--out", str(tmp_path / "t.java")]) == 0
    assert "à relire" in capsys.readouterr().out


def test_prompts_and_fences():
    assert "Points non convertis" in leftovers_prompt("A.java", "x", ["y"])
    assert strip_fences("```\nabc\n```") == "abc\n"


def test_client_reads_environment(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://h:1/")
    monkeypatch.setenv("OLLAMA_MODEL", "m")
    client = OllamaClient()
    assert (client.base_url, client.model) == ("http://h:1", "m")
