"""Tests for envault.env_transform."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_transform import (
    TransformResult,
    changed_count,
    skipped_count,
    transform_env,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PASS=Secret123\n"
        "APP_ENV=production\n"
        "LABEL=  hello world  \n"
    )
    return p


def test_transform_returns_transform_result_type(env_file: Path) -> None:
    result = transform_env(env_file, "uppercase", write=False)
    assert isinstance(result, TransformResult)


def test_uppercase_converts_values(env_file: Path) -> None:
    result = transform_env(env_file, "uppercase", write=False)
    assert result.transformed["APP_ENV"] == "PRODUCTION"
    assert result.transformed["DB_HOST"] == "LOCALHOST"


def test_lowercase_converts_values(env_file: Path) -> None:
    result = transform_env(env_file, "lowercase", write=False)
    assert result.transformed["DB_PASS"] == "secret123"


def test_strip_removes_whitespace(env_file: Path) -> None:
    result = transform_env(env_file, "strip", write=False)
    assert result.transformed["LABEL"] == "hello world"


def test_replace_operation(env_file: Path) -> None:
    result = transform_env(env_file, "replace:localhost:127.0.0.1", write=False)
    assert result.transformed["DB_HOST"] == "127.0.0.1"
    assert "DB_HOST" in result.changed_keys


def test_replace_unchanged_key_not_in_changed(env_file: Path) -> None:
    result = transform_env(env_file, "replace:localhost:127.0.0.1", write=False)
    assert "APP_ENV" not in result.changed_keys


def test_limit_to_specific_keys(env_file: Path) -> None:
    result = transform_env(env_file, "uppercase", keys=["APP_ENV"], write=False)
    assert result.transformed["APP_ENV"] == "PRODUCTION"
    # other keys must be untouched
    assert result.transformed["DB_HOST"] == "localhost"
    assert "DB_HOST" not in result.changed_keys


def test_changed_count_helper(env_file: Path) -> None:
    result = transform_env(env_file, "uppercase", write=False)
    assert changed_count(result) >= 1


def test_skipped_count_helper(env_file: Path) -> None:
    result = transform_env(env_file, "uppercase", keys=["APP_ENV"], write=False)
    # all other keys are skipped
    assert skipped_count(result) == 3


def test_write_persists_changes(env_file: Path) -> None:
    transform_env(env_file, "uppercase", write=True)
    content = env_file.read_text()
    assert "APP_ENV=PRODUCTION" in content


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        transform_env(tmp_path / "ghost.env", "uppercase")


def test_unknown_operation_raises(env_file: Path) -> None:
    with pytest.raises(ValueError, match="Unknown operation"):
        transform_env(env_file, "explode", write=False)


def test_strip_quotes_operation(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text('API_KEY="my_secret"\n')
    result = transform_env(p, "strip_quotes", write=False)
    assert result.transformed["API_KEY"] == "my_secret"
