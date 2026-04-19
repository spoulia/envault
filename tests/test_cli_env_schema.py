"""Tests for envault.cli_env_schema."""
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_schema import schema


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("PORT=8080\nDEBUG=true\n")
    return p


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    schema_data = {
        "keys": {
            "PORT": {"required": True, "type": "integer"},
            "DEBUG": {"required": True, "type": "boolean"},
        }
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema_data))
    return p


def test_check_passes(runner, env_file, schema_file):
    result = runner.invoke(schema, ["check", str(env_file), str(schema_file)])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_check_fails_on_invalid(runner, tmp_path, schema_file):
    bad_env = tmp_path / "bad.env"
    bad_env.write_text("PORT=notanumber\nDEBUG=true\n")
    result = runner.invoke(schema, ["check", str(bad_env), str(schema_file)])
    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_check_json_output(runner, env_file, schema_file):
    result = runner.invoke(schema, ["check", str(env_file), str(schema_file), "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)


def test_init_creates_schema(runner, env_file, tmp_path):
    out = tmp_path / "out.json"
    result = runner.invoke(schema, ["init", str(env_file), str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "PORT" in data["keys"]
    assert "DEBUG" in data["keys"]


def test_check_missing_required_shows_error(runner, tmp_path, schema_file):
    env = tmp_path / ".env"
    env.write_text("PORT=9000\n")
    result = runner.invoke(schema, ["check", str(env), str(schema_file)])
    assert result.exit_code == 1
    assert "DEBUG" in result.output
