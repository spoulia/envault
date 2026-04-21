"""Tests for envault.env_flatten."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_flatten import FlattenResult, flatten_env, format_flatten


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'DB_CONFIG={"host": "localhost", "port": 5432}\n'
        'TAGS=["web", "api"]\n'
        "PLAIN_KEY=hello\n"
        "EMPTY_VAL=\n"
    )
    return p


def test_flatten_returns_flatten_result_type(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert isinstance(result, FlattenResult)


def test_flatten_expands_dict_value(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert "DB_CONFIG.host" in result.flattened
    assert result.flattened["DB_CONFIG.host"] == "localhost"


def test_flatten_expands_dict_numeric_value(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert result.flattened["DB_CONFIG.port"] == "5432"


def test_flatten_expands_list_value(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert result.flattened["TAGS.0"] == "web"
    assert result.flattened["TAGS.1"] == "api"


def test_flatten_preserves_plain_values(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert result.flattened["PLAIN_KEY"] == "hello"


def test_flatten_preserves_empty_values(env_file: Path) -> None:
    result = flatten_env(env_file)
    assert "EMPTY_VAL" in result.flattened
    assert result.flattened["EMPTY_VAL"] == ""


def test_flatten_count(env_file: Path) -> None:
    result = flatten_env(env_file)
    # DB_CONFIG.host, DB_CONFIG.port, TAGS.0, TAGS.1, PLAIN_KEY, EMPTY_VAL
    assert result.flattened_count == 6


def test_flatten_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        flatten_env(tmp_path / "missing.env")


def test_format_flatten_contains_keys(env_file: Path) -> None:
    result = flatten_env(env_file)
    rendered = format_flatten(result)
    assert "DB_CONFIG.host=localhost" in rendered
    assert "TAGS.0=web" in rendered


def test_format_flatten_has_header(env_file: Path) -> None:
    result = flatten_env(env_file)
    rendered = format_flatten(result)
    assert rendered.startswith("# Flattened from")


def test_nested_dict_flattens_deeply(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text('DEEP={"a": {"b": {"c": 42}}}\n')
    result = flatten_env(p)
    assert result.flattened.get("DEEP.a.b.c") == "42"
