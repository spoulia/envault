import pytest
from pathlib import Path
from envault.env_redact import redact, redact_to_file, REDACT_PLACEHOLDER


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=supersecret\n"
        "API_KEY=abc123\n"
        "PORT=8080\n"
        "AUTH_TOKEN=tok_xyz\n"
    )
    return p


def test_redact_sensitive_keys(env_file):
    result = redact(env_file)
    assert result.redacted["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result.redacted["API_KEY"] == REDACT_PLACEHOLDER
    assert result.redacted["AUTH_TOKEN"] == REDACT_PLACEHOLDER


def test_redact_preserves_non_sensitive(env_file):
    result = redact(env_file)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"


def test_redact_keys_list(env_file):
    result = redact(env_file)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_redact_original_unchanged(env_file):
    result = redact(env_file)
    assert result.original["DB_PASSWORD"] == "supersecret"
    assert result.original["API_KEY"] == "abc123"


def test_redact_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        redact(tmp_path / "missing.env")


def test_redact_custom_pattern(env_file):
    result = redact(env_file, patterns=["PORT"])
    assert result.redacted["PORT"] == REDACT_PLACEHOLDER
    assert result.redacted["DB_PASSWORD"] == "supersecret"


def test_redact_to_file_writes_output(env_file, tmp_path):
    dest = tmp_path / "redacted.env"
    result = redact_to_file(env_file, dest)
    assert dest.exists()
    content = dest.read_text()
    assert REDACT_PLACEHOLDER in content
    assert "supersecret" not in content
    assert "myapp" in content


def test_redact_to_file_returns_result(env_file, tmp_path):
    dest = tmp_path / "redacted.env"
    result = redact_to_file(env_file, dest)
    assert len(result.redacted_keys) > 0
