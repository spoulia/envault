"""Tests for envault.env_backup."""
import time
from pathlib import Path

import pytest

import envault.env_backup as backup_mod
from envault.env_backup import (
    BackupResult,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(backup_mod, "BACKUP_DIR", tmp_path / ".envault_backups")
    yield


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nDEBUG=true\n")
    return p


def test_create_backup_returns_backup_result(env_file):
    result = create_backup(env_file)
    assert isinstance(result, BackupResult)
    assert result.source == str(env_file)


def test_create_backup_file_exists(env_file):
    result = create_backup(env_file)
    assert Path(result.backup_path).exists()


def test_create_backup_content_matches(env_file):
    result = create_backup(env_file)
    assert Path(result.backup_path).read_text() == env_file.read_text()


def test_create_backup_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(tmp_path / "nonexistent.env")


def test_list_backups_empty_when_no_backups():
    assert list_backups() == []


def test_list_backups_returns_entries(env_file):
    create_backup(env_file)
    entries = list_backups()
    assert len(entries) == 1


def test_list_backups_filtered_by_source(env_file, tmp_path):
    other = tmp_path / "other.env"
    other.write_text("X=1\n")
    create_backup(env_file)
    create_backup(other)
    entries = list_backups(source=env_file)
    assert all(e.source == env_file.stem for e in entries)
    assert len(entries) == 1


def test_restore_backup_overwrites_destination(env_file, tmp_path):
    create_backup(env_file)
    entries = list_backups()
    dest = tmp_path / "restored.env"
    restore_backup(entries[0].name, dest)
    assert dest.read_text() == env_file.read_text()


def test_restore_backup_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_backup("ghost_12345.env", tmp_path / "out.env")


def test_delete_backup_removes_file(env_file):
    create_backup(env_file)
    entries = list_backups()
    delete_backup(entries[0].name)
    assert list_backups() == []


def test_delete_backup_missing_raises():
    with pytest.raises(FileNotFoundError):
        delete_backup("missing_000.env")
