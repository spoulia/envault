"""Tests for envault.env_schema."""
import json
from pathlib import Path

import pytest

from envault.env_schema import SchemaIssue, SchemaResult, validate_schema


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_PORT=5432\nDEBUG=true\nAPP_NAME=myapp\nSCORE=3.14\n")
    return p


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    schema = {
        "keys": {
            "DB_PORT": {"required": True, "type": "integer"},
            "DEBUG": {"required": True, "type": "boolean"},
            "APP_NAME": {"required": True, "type": "string"},
            "SCORE": {"required": False, "type": "float"},
        }
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema))
    return p


def test_valid_env_passes(env_file, schema_file):
    result = validate_schema(env_file, schema_file)
    assert result.valid
    assert result.issues == []


def test_missing_required_key(tmp_path, schema_file):
    env = tmp_path / ".env"
    env.write_text("DEBUG=true\nAPP_NAME=x\nSCORE=1.0\n")
    result = validate_schema(env, schema_file)
    assert not result.valid
    keys = [i.key for i in result.issues]
    assert "DB_PORT" in keys


def test_wrong_type_integer(tmp_path, schema_file):
    env = tmp_path / ".env"
    env.write_text("DB_PORT=notanint\nDEBUG=true\nAPP_NAME=x\n")
    result = validate_schema(env, schema_file)
    assert not result.valid
    assert any(i.key == "DB_PORT" for i in result.issues)


def test_wrong_type_boolean(tmp_path, schema_file):
    env = tmp_path / ".env"
    env.write_text("DB_PORT=5432\nDEBUG=maybe\nAPP_NAME=x\n")
    result = validate_schema(env, schema_file)
    assert not result.valid
    assert any(i.key == "DEBUG" for i in result.issues)


def test_allowed_values_violation(tmp_path, tmp_path_factory):
    schema_path = tmp_path / "schema.json"
    schema = {"keys": {"ENV": {"required": True, "allowed": ["prod", "staging", "dev"]}}}
    schema_path.write_text(json.dumps(schema))
    env = tmp_path / ".env"
    env.write_text("ENV=local\n")
    result = validate_schema(env, schema_path)
    assert not result.valid
    assert any(i.key == "ENV" for i in result.issues)


def test_pattern_violation(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema = {"keys": {"VERSION": {"required": True, "pattern": r"\d+\.\d+\.\d+"}}}
    schema_path.write_text(json.dumps(schema))
    env = tmp_path / ".env"
    env.write_text("VERSION=not-a-version\n")
    result = validate_schema(env, schema_path)
    assert not result.valid


def test_missing_env_file_raises(tmp_path):
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps({"keys": {}}))
    with pytest.raises(FileNotFoundError):
        validate_schema(tmp_path / "missing.env", schema_path)


def test_schema_result_type():
    r = SchemaResult()
    assert r.valid
    r.issues.append(SchemaIssue("KEY", "bad"))
    assert not r.valid
