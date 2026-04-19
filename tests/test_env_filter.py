"""Tests for envault.env_filter."""
import pytest
from pathlib import Path

from envault.env_filter import filter_keys, FilterResult


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "APP_SECRET=abc123\n"
        "APP_DEBUG=true\n"
        "LOG_LEVEL=info\n"
    )
    return f


def test_filter_by_key(env_file):
    r = filter_keys(env_file, keys=["DB_HOST", "LOG_LEVEL"])
    assert set(r.kept) == {"DB_HOST", "LOG_LEVEL"}
    assert "APP_SECRET" in r.removed


def test_filter_by_prefix(env_file):
    r = filter_keys(env_file, prefix="DB_")
    assert set(r.kept) == {"DB_HOST", "DB_PORT"}


def test_filter_by_pattern(env_file):
    r = filter_keys(env_file, pattern="APP_*")
    assert set(r.kept) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_exclude_mode(env_file):
    r = filter_keys(env_file, prefix="DB_", exclude=True)
    assert "DB_HOST" not in r.kept
    assert "DB_PORT" not in r.kept
    assert "APP_SECRET" in r.kept


def test_filter_no_criteria_keeps_all(env_file):
    r = filter_keys(env_file)
    assert r.kept_count == 5
    assert r.removed_count == 0


def test_filter_write(env_file):
    filter_keys(env_file, prefix="APP_", write=True)
    content = env_file.read_text()
    assert "APP_SECRET" in content
    assert "DB_HOST" not in content


def test_filter_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        filter_keys(tmp_path / "missing.env", keys=["X"])


def test_filter_result_counts(env_file):
    r = filter_keys(env_file, prefix="DB_")
    assert r.kept_count == 2
    assert r.removed_count == 3


def test_filter_returns_filter_result(env_file):
    r = filter_keys(env_file, keys=["LOG_LEVEL"])
    assert isinstance(r, FilterResult)
