"""Tests for envault.env_whitelist."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_whitelist import whitelist_file, WhitelistResult


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "APP_SECRET=s3cr3t\n"
        "DEBUG=true\n"
        "REDIS_URL=redis://localhost\n"
    )
    return p


def test_whitelist_returns_whitelist_result_type(env_file: Path) -> None:
    result = whitelist_file(env_file, ["DB_HOST"])
    assert isinstance(result, WhitelistResult)


def test_whitelist_keeps_exact_key(env_file: Path) -> None:
    result = whitelist_file(env_file, ["DB_HOST", "DEBUG"])
    assert "DB_HOST" in result.kept
    assert "DEBUG" in result.kept


def test_whitelist_removes_other_keys(env_file: Path) -> None:
    result = whitelist_file(env_file, ["DB_HOST"])
    assert "APP_SECRET" in result.removed
    assert "REDIS_URL" in result.removed


def test_whitelist_pattern_keeps_prefix(env_file: Path) -> None:
    result = whitelist_file(env_file, [], patterns=["DB_*"])
    assert "DB_HOST" in result.kept
    assert "DB_PORT" in result.kept
    assert "APP_SECRET" in result.removed


def test_whitelist_writes_file(env_file: Path) -> None:
    whitelist_file(env_file, ["DEBUG"])
    content = env_file.read_text()
    assert "DEBUG=true" in content
    assert "DB_HOST" not in content


def test_whitelist_output_file(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.env"
    whitelist_file(env_file, ["APP_SECRET"], output=out)
    assert out.exists()
    assert "APP_SECRET" in out.read_text()
    # source should be unchanged
    assert "DB_HOST" in env_file.read_text()


def test_whitelist_counts(env_file: Path) -> None:
    result = whitelist_file(env_file, ["DB_HOST", "DB_PORT"])
    assert result.kept_count == 2
    assert result.removed_count == 3


def test_whitelist_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        whitelist_file(tmp_path / "ghost.env", ["KEY"])


def test_whitelist_combined_keys_and_patterns(env_file: Path) -> None:
    result = whitelist_file(env_file, ["DEBUG"], patterns=["REDIS_*"])
    assert "DEBUG" in result.kept
    assert "REDIS_URL" in result.kept
    assert "APP_SECRET" in result.removed
