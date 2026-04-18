"""Tests for envault.rotation and envault.cli_rotation."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.vault import lock, unlock
from envault.rotation import rotate, rotate_and_backup
from envault.cli_rotation import rotation


ENV_CONTENT = b"DB_URL=postgres://localhost/test\nSECRET=abc123\n"
OLD_PASS = "old-hunter2"
NEW_PASS = "new-hunter2"


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    path = tmp_path / ".envault"
    env_file = tmp_path / ".env"
    env_file.write_bytes(ENV_CONTENT)
    lock(env_file, path, OLD_PASS)
    return path


def test_rotate_allows_unlock_with_new_password(vault_file: Path, tmp_path: Path) -> None:
    rotate(vault_file, OLD_PASS, NEW_PASS)
    out = tmp_path / ".env.out"
    unlock(vault_file, out, NEW_PASS)
    assert out.read_bytes() == ENV_CONTENT


def test_rotate_old_password_no_longer_works(vault_file: Path, tmp_path: Path) -> None:
    rotate(vault_file, OLD_PASS, NEW_PASS)
    out = tmp_path / ".env.out"
    with pytest.raises(ValueError):
        unlock(vault_file, out, OLD_PASS)


def test_rotate_wrong_old_password_raises(vault_file: Path) -> None:
    with pytest.raises(ValueError):
        rotate(vault_file, "wrong", NEW_PASS)


def test_rotate_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        rotate(tmp_path / "missing.envault", OLD_PASS, NEW_PASS)


def test_rotate_and_backup_creates_bak(vault_file: Path) -> None:
    bak = rotate_and_backup(vault_file, OLD_PASS, NEW_PASS)
    assert bak.exists()
    assert bak.suffix == ".bak"


def test_rotate_and_backup_bak_decryptable_with_old_password(vault_file: Path, tmp_path: Path) -> None:
    bak = rotate_and_backup(vault_file, OLD_PASS, NEW_PASS)
    out = tmp_path / ".env.bak.out"
    unlock(bak, out, OLD_PASS)
    assert out.read_bytes() == ENV_CONTENT


# --- CLI tests ---


def test_cli_rotate_success(vault_file: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        rotation,
        ["rotate", "--vault", str(vault_file), "--old-password", OLD_PASS, "--new-password", NEW_PASS],
    )
    assert result.exit_code == 0
    assert "successful" in result.output


def test_cli_rotate_wrong_password_shows_error(vault_file: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        rotation,
        ["rotate", "--vault", str(vault_file), "--old-password", "bad", "--new-password", NEW_PASS],
    )
    assert result.exit_code != 0
    assert "incorrect" in result.output


def test_cli_rotate_missing_vault_shows_error(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        rotation,
        ["rotate", "--vault", str(tmp_path / "no.envault"), "--old-password", OLD_PASS, "--new-password", NEW_PASS],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
