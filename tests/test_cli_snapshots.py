"""Tests for envault.cli_snapshots."""
import pytest
from click.testing import CliRunner
from pathlib import Path

import envault.snapshots as snap_mod
from envault.cli_snapshots import snapshots


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(snap_mod, "SNAPSHOT_DIR", tmp_path / "snaps")
    monkeypatch.setattr(snap_mod, "_META_FILE", tmp_path / "snaps" / "meta.json")
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".env.vault"
    v.write_bytes(b"fake-vault-bytes")
    return v


def test_save_snapshot_success(runner, vault_file):
    result = runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file)])
    assert result.exit_code == 0
    assert "v1" in result.output


def test_save_snapshot_missing_vault(runner, tmp_path):
    result = runner.invoke(snapshots, ["save", "v1", "--vault", str(tmp_path / "missing.vault")])
    assert result.exit_code == 0
    assert "Error" in result.output


def test_save_duplicate_shows_error(runner, vault_file):
    runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file)])
    result = runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file)])
    assert "Error" in result.output


def test_restore_snapshot(runner, vault_file, tmp_path):
    runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file)])
    target = tmp_path / "out.vault"
    result = runner.invoke(snapshots, ["restore", "v1", "--vault", str(target)])
    assert result.exit_code == 0
    assert "restored" in result.output
    assert target.read_bytes() == vault_file.read_bytes()


def test_restore_unknown_shows_error(runner):
    result = runner.invoke(snapshots, ["restore", "ghost"])
    assert "Error" in result.output


def test_list_empty(runner):
    result = runner.invoke(snapshots, ["list"])
    assert "No snapshots" in result.output


def test_list_shows_entries(runner, vault_file):
    runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file), "--desc", "first"])
    result = runner.invoke(snapshots, ["list"])
    assert "v1" in result.output
    assert "first" in result.output


def test_delete_snapshot(runner, vault_file):
    runner.invoke(snapshots, ["save", "v1", "--vault", str(vault_file)])
    result = runner.invoke(snapshots, ["delete", "v1"])
    assert "deleted" in result.output
