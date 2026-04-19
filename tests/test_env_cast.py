"""Tests for envault.env_cast."""
from pathlib import Path
import pytest
from envault.env_cast import cast_env, CastResult


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "PORT=8080\n"
        "DEBUG=true\n"
        "RATIO=3.14\n"
        "NAME=envault\n"
        "ENABLED=false\n"
    )
    return f


def test_cast_int(env_file):
    result = cast_env(env_file, {"PORT": "int"})
    assert result.casted["PORT"] == 8080
    assert isinstance(result.casted["PORT"], int)


def test_cast_float(env_file):
    result = cast_env(env_file, {"RATIO": "float"})
    assert result.casted["RATIO"] == pytest.approx(3.14)


def test_cast_bool_true(env_file):
    result = cast_env(env_file, {"DEBUG": "bool"})
    assert result.casted["DEBUG"] is True


def test_cast_bool_false(env_file):
    result = cast_env(env_file, {"ENABLED": "bool"})
    assert result.casted["ENABLED"] is False


def test_cast_str_default(env_file):
    result = cast_env(env_file, {"NAME": "str"})
    assert result.casted["NAME"] == "envault"


def test_uncasted_key_in_skipped(env_file):
    result = cast_env(env_file, {"PORT": "int"})
    assert "NAME" in result.skipped


def test_invalid_int_records_error(tmp_path):
    f = tmp_path / ".env"
    f.write_text("PORT=notanumber\n")
    result = cast_env(f, {"PORT": "int"})
    assert result.errors
    assert "PORT" in result.errors[0]


def test_unsupported_type_records_error(env_file):
    result = cast_env(env_file, {"PORT": "list"})
    assert any("unsupported type" in e for e in result.errors)


def test_cast_result_type(env_file):
    result = cast_env(env_file, {})
    assert isinstance(result, CastResult)


def test_multiple_rules(env_file):
    result = cast_env(env_file, {"PORT": "int", "RATIO": "float", "DEBUG": "bool"})
    assert result.casted["PORT"] == 8080
    assert result.casted["RATIO"] == pytest.approx(3.14)
    assert result.casted["DEBUG"] is True
    assert not result.errors
