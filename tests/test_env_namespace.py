"""Tests for envault.env_namespace."""
import pytest
from pathlib import Path

from envault.env_namespace import (
    add_namespace,
    strip_namespace,
    list_namespaces,
    NamespaceResult,
)


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\nSECRET=abc123\n")
    return f


def test_add_namespace_prefixes_keys(env_file):
    result = add_namespace(env_file, "PROD_")
    assert "DB_HOST" in result.affected
    assert "DB_PORT" in result.affected
    assert "APP_NAME" in result.affected
    assert "SECRET" in result.affected
    assert result.affected_count == 4


def test_add_namespace_writes_file(env_file):
    add_namespace(env_file, "PROD_")
    content = env_file.read_text()
    assert "PROD_DB_HOST=localhost" in content
    assert "PROD_SECRET=abc123" in content


def test_add_namespace_skips_already_prefixed(env_file):
    add_namespace(env_file, "DB_")
    result = add_namespace(env_file, "DB_")
    assert "DB_HOST" in result.skipped
    assert "DB_PORT" in result.skipped


def test_add_namespace_returns_namespace_result_type(env_file):
    result = add_namespace(env_file, "X_")
    assert isinstance(result, NamespaceResult)


def test_strip_namespace_removes_prefix(env_file):
    add_namespace(env_file, "PROD_")
    result = strip_namespace(env_file, "PROD_")
    assert result.affected_count == 4
    content = env_file.read_text()
    assert "DB_HOST=localhost" in content
    assert "PROD_" not in content


def test_strip_namespace_skips_non_matching(env_file):
    result = strip_namespace(env_file, "MISSING_")
    assert result.affected_count == 0
    assert result.skipped_count == 4


def test_strip_namespace_returns_namespace_result_type(env_file):
    result = strip_namespace(env_file, "DB_")
    assert isinstance(result, NamespaceResult)


def test_list_namespaces_groups_by_prefix(env_file):
    buckets = list_namespaces(env_file)
    assert "DB_" in buckets
    assert "DB_HOST" in buckets["DB_"]
    assert "DB_PORT" in buckets["DB_"]


def test_list_namespaces_no_underscore_goes_to_none(tmp_path):
    f = tmp_path / ".env"
    f.write_text("SIMPLE=value\n")
    buckets = list_namespaces(f)
    assert "(none)" in buckets
    assert "SIMPLE" in buckets["(none)"]


def test_add_then_strip_roundtrip(env_file):
    original = env_file.read_text()
    add_namespace(env_file, "NS_")
    strip_namespace(env_file, "NS_")
    assert env_file.read_text() == original


def test_add_namespace_raises_for_missing_file(tmp_path):
    """add_namespace should raise FileNotFoundError when the env file does not exist."""
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(FileNotFoundError):
        add_namespace(missing, "PROD_")


def test_strip_namespace_raises_for_missing_file(tmp_path):
    """strip_namespace should raise FileNotFoundError when the env file does not exist."""
    missing = tmp_path / "nonexistent.env"
    with pytest.raises(FileNotFoundError):
        strip_namespace(missing, "PROD_")
