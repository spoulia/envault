"""Tests for envault.cli_env_required."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_required import required_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nAPI_KEY=secret\nEMPTY_VAL=\n")
    return p


def test_check_all_present_exits_zero(runner: CliRunner, env_file: Path):
    result = runner.invoke(required_cmd, ["check", str(env_file), "-k", "DB_HOST", "-k", "API_KEY"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_missing_key_exits_nonzero(runner: CliRunner, env_file: Path):
    result = runner.invoke(required_cmd, ["check", str(env_file), "-k", "DOES_NOT_EXIST"])
    assert result.exit_code != 0
    assert "MISSING" in (result.output + (result.stderr if hasattr(result, 'stderr') else ""))


def test_check_empty_value_exits_nonzero(runner: CliRunner, env_file: Path):
    result = runner.invoke(required_cmd, ["check", str(env_file), "-k", "EMPTY_VAL"])
    assert result.exit_code != 0


def test_check_allow_empty_flag_exits_zero(runner: CliRunner, env_file: Path):
    result = runner.invoke(
        required_cmd,
        ["check", str(env_file), "-k", "EMPTY_VAL", "--allow-empty"],
    )
    assert result.exit_code == 0


def test_check_missing_file_exits_nonzero(runner: CliRunner, tmp_path: Path):
    ghost = tmp_path / "ghost.env"
    result = runner.invoke(required_cmd, ["check", str(ghost), "-k", "ANY_KEY"])
    assert result.exit_code != 0
