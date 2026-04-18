"""Tests for envault.env_validate and cli_validate."""
from pathlib import Path
import pytest
from click.testing import CliRunner

from envault.env_validate import validate_file, ValidationResult
from envault.cli_validate import validate


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=\nAPI_KEY=abc123\n")
    return f


def test_clean_file_no_required_rules(env_file):
    result = validate_file(env_file)
    assert result.ok
    assert result.issues == []


def test_required_key_present(env_file):
    result = validate_file(env_file, required=["DB_HOST"])
    assert result.ok


def test_required_key_missing(env_file):
    result = validate_file(env_file, required=["MISSING_KEY"])
    assert not result.ok
    assert any(i.key == "MISSING_KEY" for i in result.issues)


def test_nonempty_violation(env_file):
    result = validate_file(env_file, nonempty=["SECRET"])
    assert not result.ok
    assert any(i.key == "SECRET" and i.severity == "error" for i in result.issues)


def test_pattern_match_passes(env_file):
    result = validate_file(env_file, patterns={"DB_PORT": r"\d+"})
    assert result.ok


def test_pattern_mismatch_warning(env_file):
    result = validate_file(env_file, patterns={"DB_HOST": r"\d+"})
    assert result.ok  # warning, not error
    assert any(i.key == "DB_HOST" and i.severity == "warning" for i in result.issues)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_file(tmp_path / "nonexistent.env")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_check_clean(runner, env_file):
    res = runner.invoke(validate, ["check", str(env_file)])
    assert "No issues found" in res.output
    assert res.exit_code == 0


def test_cli_check_missing_required(runner, env_file):
    res = runner.invoke(validate, ["check", str(env_file), "--required", "GHOST"])
    assert "GHOST" in res.output
    assert res.exit_code == 1


def test_cli_check_json_output(runner, env_file):
    import json
    res = runner.invoke(validate, ["check", str(env_file), "--required", "GHOST", "--json"])
    data = json.loads(res.output)
    assert isinstance(data, list)
    assert data[0]["key"] == "GHOST"
