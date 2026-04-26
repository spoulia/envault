"""Tests for envault.env_supersede."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_supersede import SupersedeResult, supersede


@pytest.fixture()
def env_pair(tmp_path: Path):
    src = tmp_path / "source.env"
    dst = tmp_path / "target.env"
    src.write_text("DB_HOST=prod-db\nDB_PORT=5432\nNEW_KEY=hello\n")
    dst.write_text("DB_HOST=localhost\nDB_PORT=5432\nEXTRA=keep\n")
    return src, dst


def test_supersede_returns_result_type(env_pair):
    src, dst = env_pair
    result = supersede(src, dst)
    assert isinstance(result, SupersedeResult)


def test_supersede_overwrites_existing_key(env_pair):
    src, dst = env_pair
    supersede(src, dst)
    lines = dst.read_text().splitlines()
    assert "DB_HOST=prod-db" in lines


def test_supersede_adds_missing_key_by_default(env_pair):
    src, dst = env_pair
    supersede(src, dst)
    lines = dst.read_text().splitlines()
    assert "NEW_KEY=hello" in lines


def test_supersede_no_add_skips_missing_key(env_pair):
    src, dst = env_pair
    result = supersede(src, dst, add_missing=False)
    assert "NEW_KEY" in result.skipped
    lines = dst.read_text().splitlines()
    assert not any(l.startswith("NEW_KEY") for l in lines)


def test_supersede_no_overwrite_skips_existing(env_pair):
    src, dst = env_pair
    result = supersede(src, dst, overwrite=False)
    assert "DB_HOST" in result.skipped
    lines = dst.read_text().splitlines()
    assert "DB_HOST=localhost" in lines


def test_supersede_specific_keys_only(env_pair):
    src, dst = env_pair
    result = supersede(src, dst, keys=["DB_HOST"])
    assert result.applied == ["DB_HOST"]
    assert "NEW_KEY" not in result.added


def test_supersede_preserves_target_only_keys(env_pair):
    src, dst = env_pair
    supersede(src, dst)
    lines = dst.read_text().splitlines()
    assert "EXTRA=keep" in lines


def test_supersede_dry_run_does_not_write(env_pair):
    src, dst = env_pair
    original = dst.read_text()
    supersede(src, dst, dry_run=True)
    assert dst.read_text() == original


def test_supersede_missing_source_raises(tmp_path: Path):
    dst = tmp_path / "target.env"
    dst.write_text("KEY=val\n")
    with pytest.raises(FileNotFoundError, match="Source"):
        supersede(tmp_path / "missing.env", dst)


def test_supersede_missing_target_raises(tmp_path: Path):
    src = tmp_path / "source.env"
    src.write_text("KEY=val\n")
    with pytest.raises(FileNotFoundError, match="Target"):
        supersede(src, tmp_path / "missing.env")


def test_applied_count_property(env_pair):
    src, dst = env_pair
    result = supersede(src, dst)
    assert result.applied_count == len(result.applied)
    assert result.added_count == len(result.added)
