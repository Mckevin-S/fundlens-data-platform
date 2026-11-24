from code_guard.config import Config
from code_guard.rules.secrets import check_secrets


def scan(repo, rel, text):
    return [f.message for f in check_secrets(repo(rel, text), text, Config(root=repo.root))]


def test_detects_aws_key_private_key_github_token_and_password(repo):
    text = "\n".join([
        "aws_key = AKIAABCDEFGHIJKLMNOP",
        "-----BEGIN RSA PRIVATE KEY-----",
        "token: ghp_" + "a" * 36,
        'spring.datasource.password = "SuperSecret123"',
    ])
    assert len(scan(repo, "app.properties", text)) == 4


def test_placeholders_and_short_values_are_ignored(repo):
    text = 'password = "${DB_PASSWORD}"\nsecret = "short"\n'
    assert scan(repo, "app.yml", text) == []


def test_allowlisted_example_file_is_ignored(repo):
    assert scan(repo, ".env.example", 'API_KEY="changeme-changeme"') == []
