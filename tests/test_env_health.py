"""Tests for envault.env_health."""
import pytest
from pathlib import Path
from envault.env_health import check_health, HealthResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    yield p


def _write(p: Path, content: str):
    p.write_text(content)


def test_healthy_file_returns_no_issues(env_file):
    _write(env_file, "DB_HOST=localhost\nDB_PORT=5432\n")
    result = check_health(env_file)
    assert isinstance(result, HealthResult)
    assert result.healthy
    assert result.issues == []


def test_missing_file_returns_error(tmp_path):
    result = check_health(tmp_path / "missing.env")
    assert not result.healthy
    assert any("not found" in i.message for i in result.issues)


def test_missing_separator_is_error(env_file):
    _write(env_file, "BADLINE\nGOOD=val\n")
    result = check_health(env_file)
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 1
    assert "missing '='" in errors[0].message


def test_lowercase_key_is_warning(env_file):
    _write(env_file, "my_key=value\n")
    result = check_health(env_file)
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any("uppercase" in w.message for w in warnings)


def test_duplicate_key_is_warning(env_file):
    _write(env_file, "FOO=1\nFOO=2\n")
    result = check_health(env_file)
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any("Duplicate" in w.message for w in warnings)


def test_placeholder_value_is_info(env_file):
    _write(env_file, "SECRET=CHANGE_ME\n")
    result = check_health(env_file)
    infos = [i for i in result.issues if i.level == "info"]
    assert any("placeholder" in i.message for i in infos)


def test_empty_value_is_info(env_file):
    _write(env_file, "TOKEN=\n")
    result = check_health(env_file)
    infos = [i for i in result.issues if i.level == "info"]
    assert len(infos) == 1


def test_total_keys_count(env_file):
    _write(env_file, "# comment\nA=1\nB=2\nC=3\n")
    result = check_health(env_file)
    assert result.total_keys == 3


def test_healthy_property_false_when_errors(env_file):
    _write(env_file, "NOEQUALSSIGN\n")
    result = check_health(env_file)
    assert not result.healthy
