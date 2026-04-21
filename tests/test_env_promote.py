"""Tests for envault.env_promote."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_promote import PromoteResult, promote_keys


@pytest.fixture()
def src_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.staging"
    p.write_text("DB_HOST=staging-db\nDB_PORT=5432\nSECRET_KEY=abc123\n")
    return p


@pytest.fixture()
def dst_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.production"
    p.write_text("DB_HOST=prod-db\nAPP_ENV=production\n")
    return p


def test_promote_all_keys(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file, overwrite=True)
    assert "DB_HOST" in result.promoted
    assert "DB_PORT" in result.promoted
    assert "SECRET_KEY" in result.promoted


def test_promote_returns_promote_result_type(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file)
    assert isinstance(result, PromoteResult)


def test_promote_specific_keys(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file, keys=["DB_PORT", "SECRET_KEY"])
    assert result.promoted == ["DB_PORT", "SECRET_KEY"]


def test_promote_skips_existing_without_overwrite(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file)
    assert "DB_HOST" in result.skipped


def test_promote_overwrites_when_flag_set(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file, keys=["DB_HOST"], overwrite=True)
    assert "DB_HOST" in result.promoted
    content = dst_file.read_text()
    assert "DB_HOST=staging-db" in content


def test_promote_writes_new_key_to_dst(src_file: Path, dst_file: Path) -> None:
    promote_keys(src_file, dst_file, keys=["DB_PORT"])
    content = dst_file.read_text()
    assert "DB_PORT=5432" in content


def test_promote_missing_src_raises(tmp_path: Path, dst_file: Path) -> None:
    missing = tmp_path / "missing.env"
    with pytest.raises(FileNotFoundError):
        promote_keys(missing, dst_file)


def test_promote_missing_dst_raises(src_file: Path, tmp_path: Path) -> None:
    missing = tmp_path / "missing.env"
    with pytest.raises(FileNotFoundError):
        promote_keys(src_file, missing)


def test_promote_skips_unknown_key(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped
    assert result.promoted_count == 0


def test_promote_source_and_destination_recorded(src_file: Path, dst_file: Path) -> None:
    result = promote_keys(src_file, dst_file)
    assert str(src_file) == result.source
    assert str(dst_file) == result.destination
