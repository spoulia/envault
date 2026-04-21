"""Tests for envault.env_patch and envault.cli_env_patch."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_patch import PatchResult, patch_file
from envault.cli_env_patch import patch_cmd


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nDEBUG=true\n")
    return p


# ---------------------------------------------------------------------------
# Unit tests – patch_file
# ---------------------------------------------------------------------------

def test_patch_returns_patch_result_type(env_file: Path) -> None:
    result = patch_file(env_file, overrides={"DB_HOST": "prod.db"})
    assert isinstance(result, PatchResult)


def test_patch_applies_new_key(env_file: Path) -> None:
    result = patch_file(env_file, overrides={"NEW_KEY": "hello"})
    assert "NEW_KEY" in result.applied
    assert "NEW_KEY=hello" in env_file.read_text()


def test_patch_overwrites_existing_key(env_file: Path) -> None:
    result = patch_file(env_file, overrides={"DB_HOST": "prod.db"})
    assert "DB_HOST" in result.applied
    assert "DB_HOST=prod.db" in env_file.read_text()


def test_patch_skips_existing_when_no_overwrite(env_file: Path) -> None:
    result = patch_file(env_file, overrides={"DB_HOST": "prod.db"}, overwrite=False)
    assert "DB_HOST" in result.skipped
    assert result.applied_count == 0
    assert "DB_HOST=localhost" in env_file.read_text()


def test_patch_removes_key(env_file: Path) -> None:
    result = patch_file(env_file, overrides={}, remove_keys=["DEBUG"])
    assert "DEBUG" in result.removed
    assert "DEBUG" not in env_file.read_text()


def test_patch_remove_missing_key_ignored(env_file: Path) -> None:
    result = patch_file(env_file, overrides={}, remove_keys=["NONEXISTENT"])
    assert result.removed_count == 0


def test_patch_writes_to_output_path(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "patched.env"
    patch_file(env_file, overrides={"DB_HOST": "remote"}, output_path=out)
    assert out.exists()
    assert "DB_HOST=remote" in out.read_text()
    # original unchanged
    assert "DB_HOST=localhost" in env_file.read_text()


def test_patch_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        patch_file(tmp_path / "ghost.env", overrides={"X": "1"})


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_patch_applies_key(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(patch_cmd, ["run", str(env_file), "-s", "DB_HOST=prod"])
    assert result.exit_code == 0
    assert "Applied" in result.output
    assert "DB_HOST=prod" in env_file.read_text()


def test_cli_patch_removes_key(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(patch_cmd, ["run", str(env_file), "-r", "DEBUG"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_cli_patch_no_overwrite_shows_skipped(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(
        patch_cmd, ["run", str(env_file), "-s", "DB_HOST=other", "--no-overwrite"]
    )
    assert result.exit_code == 0
    assert "Skipped" in result.output


def test_cli_patch_invalid_pair_errors(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(patch_cmd, ["run", str(env_file), "-s", "BADFORMAT"])
    assert result.exit_code != 0
