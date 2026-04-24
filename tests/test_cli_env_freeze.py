"""Tests for envault.cli_env_freeze."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_freeze import freeze_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("SECRET=hunter2\nHOST=localhost\nPORT=5432\n")
    return p


def test_snap_creates_freeze_file(runner: CliRunner, env_file: Path) -> None:
    with runner.isolated_filesystem(temp_dir=env_file.parent):
        result = runner.invoke(freeze_cmd, ["snap", str(env_file)])
    assert result.exit_code == 0
    assert "Frozen 3 keys" in result.output


def test_snap_custom_output(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "my.freeze.json"
    result = runner.invoke(freeze_cmd, ["snap", str(env_file), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_snap_missing_file_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(freeze_cmd, ["snap", str(tmp_path / "ghost.env")])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_drift_no_drift_message(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(freeze_cmd, ["snap", str(env_file)])
    result = runner.invoke(freeze_cmd, ["drift", str(env_file)])
    assert result.exit_code == 0
    assert "No drift" in result.output


def test_drift_reports_changed_key(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(freeze_cmd, ["snap", str(env_file)])
    env_file.write_text("SECRET=changed!\nHOST=localhost\nPORT=5432\n")
    result = runner.invoke(freeze_cmd, ["drift", str(env_file)])
    assert "SECRET" in result.output
    assert "changed" in result.output


def test_drift_strict_exits_nonzero_on_drift(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(freeze_cmd, ["snap", str(env_file)])
    env_file.write_text("SECRET=changed!\nHOST=localhost\nPORT=5432\n")
    result = runner.invoke(freeze_cmd, ["drift", str(env_file), "--strict"])
    assert result.exit_code != 0


def test_drift_missing_freeze_shows_error(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    result = runner.invoke(
        freeze_cmd,
        ["drift", str(env_file), "--freeze-file", str(tmp_path / "missing.json")],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
