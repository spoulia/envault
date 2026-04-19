"""Tests for envault.cli_env_cast."""
from pathlib import Path
import json
import pytest
from click.testing import CliRunner
from envault.cli_env_cast import cast


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("PORT=9000\nDEBUG=true\nNAME=test\n")
    return f


def test_cast_int_output(runner, env_file):
    result = runner.invoke(cast, ["run", str(env_file), "-r", "PORT:int"])
    assert result.exit_code == 0
    assert "9000" in result.output
    assert "int" in result.output


def test_cast_bool_output(runner, env_file):
    result = runner.invoke(cast, ["run", str(env_file), "-r", "DEBUG:bool"])
    assert result.exit_code == 0
    assert "True" in result.output


def test_cast_json_output(runner, env_file):
    result = runner.invoke(cast, ["run", str(env_file), "-r", "PORT:int", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["PORT"] == 9000


def test_cast_invalid_value_shows_error(runner, tmp_path):
    f = tmp_path / ".env"
    f.write_text("PORT=abc\n")
    result = runner.invoke(cast, ["run", str(f), "-r", "PORT:int"])
    assert result.exit_code == 0
    assert "error" in result.output.lower()


def test_cast_bad_rule_format(runner, env_file):
    result = runner.invoke(cast, ["run", str(env_file), "-r", "PORTINT"])
    assert result.exit_code != 0


def test_skipped_keys_message(runner, env_file):
    result = runner.invoke(cast, ["run", str(env_file), "-r", "PORT:int"])
    assert "not in rules" in result.output
