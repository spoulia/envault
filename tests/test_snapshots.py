"""Tests for envault.snapshots."""
import pytest
from pathlib import Path

import envault.snapshots as snap_mod
from envault.snapshots import (
    save_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
    get_snapshot,
)


@pytest.fixture(autouse=True)
def isolated_snapshots(tmp_path, monkeypatch):
    monkeypatch.setattr(snap_mod, "SNAPSHOT_DIR", tmp_path / "snaps")
    monkeypatch.setattr(snap_mod, "_META_FILE", tmp_path / "snaps" / "meta.json")
    yield tmp_path


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".env.vault"
    v.write_bytes(b"encrypted-content-abc")
    return v


def test_save_snapshot_creates_entry(vault_file):
    entry = save_snapshot(vault_file, "snap1")
    assert entry["name"] == "snap1"
    assert "created_at" in entry


def test_save_snapshot_persists(vault_file):
    save_snapshot(vault_file, "snap1", description="initial")
    snaps = list_snapshots()
    assert len(snaps) == 1
    assert snaps[0]["description"] == "initial"


def test_save_duplicate_raises(vault_file):
    save_snapshot(vault_file, "snap1")
    with pytest.raises(ValueError, match="already exists"):
        save_snapshot(vault_file, "snap1")


def test_save_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        save_snapshot(tmp_path / "ghost.vault", "snap1")


def test_restore_snapshot(vault_file, tmp_path):
    save_snapshot(vault_file, "snap1")
    target = tmp_path / "restored.vault"
    restore_snapshot("snap1", target)
    assert target.read_bytes() == vault_file.read_bytes()


def test_restore_unknown_raises(tmp_path):
    with pytest.raises(KeyError):
        restore_snapshot("ghost", tmp_path / "x.vault")


def test_delete_snapshot(vault_file):
    save_snapshot(vault_file, "snap1")
    delete_snapshot("snap1")
    assert list_snapshots() == []


def test_delete_unknown_raises():
    with pytest.raises(KeyError):
        delete_snapshot("ghost")


def test_get_snapshot(vault_file):
    save_snapshot(vault_file, "snap1", description="desc")
    s = get_snapshot("snap1")
    assert s["description"] == "desc"


def test_list_snapshots_empty():
    assert list_snapshots() == []
