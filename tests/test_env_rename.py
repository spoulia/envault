"""Tests for envault.env_rename."""
from pathlib import Path

import pytest

from envault.env_rename import rename_keys, RenameResult


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=production\n")
    return f


def test_rename_single_key(env_file: Path):
    result = rename_keys(env_file, {"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.renamed
    content = env_file.read_text()
    assert "DATABASE_HOST=localhost" in content
    assert "DB_HOST" not in content


def test_rename_multiple_keys(env_file: Path):
    result = rename_keys(env_file, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert len(result.renamed) == 2
    content = env_file.read_text()
    assert "DATABASE_HOST=localhost" in content
    assert "DATABASE_PORT=5432" in content


def test_rename_not_found_key(env_file: Path):
    result = rename_keys(env_file, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.not_found
    assert result.renamed == []


def test_rename_skips_when_target_exists(env_file: Path):
    result = rename_keys(env_file, {"DB_HOST": "DB_PORT"})
    assert "DB_HOST" in result.skipped
    content = env_file.read_text()
    assert "DB_HOST=localhost" in content


def test_rename_overwrite_existing(env_file: Path):
    result = rename_keys(env_file, {"DB_HOST": "DB_PORT"}, overwrite=True)
    assert ("DB_HOST", "DB_PORT") in result.renamed


def test_rename_writes_to_dst(env_file: Path, tmp_path: Path):
    dst = tmp_path / "out.env"
    rename_keys(env_file, {"DB_HOST": "DATABASE_HOST"}, dst=dst)
    assert dst.exists()
    assert "DATABASE_HOST=localhost" in dst.read_text()
    # source unchanged
    assert "DB_HOST=localhost" in env_file.read_text()


def test_rename_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        rename_keys(tmp_path / "ghost.env", {"A": "B"})


def test_rename_result_type(env_file: Path):
    result = rename_keys(env_file, {"DB_HOST": "DATABASE_HOST"})
    assert isinstance(result, RenameResult)
