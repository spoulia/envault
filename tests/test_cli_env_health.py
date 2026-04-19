"""Tests for envault.cli_env_health."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_env_health import health_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    yield p


def test_check_healthy_file(runner, env_file):
    env_file.write_text("DB=localhost\nPORT=5432\n")
    result = runner.invoke(health_cmd, ["check", str(env_file)])
    assert result.exit_code == 0
    assert "healthy" in result.output


def test_check_shows_errors(runner, env_file):
    env_file.write_text("BADLINE\n")
    result = runner.invoke(health_cmd, ["check", str(env_file)])
    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_check_shows_warnings(runner, env_file):
    env_file.write_text("lowercase=val\n")
    result = runner.invoke(health_cmd, ["check", str(env_file)])
    assert "WARNING" in result.output


def test_strict_exits_nonzero_on_warnings(runner, env_file):
    env_file.write_text("lowercase=val\n")
    result = runner.invoke(health_cmd, ["check", "--strict", str(env_file)])
    assert result.exit_code == 1


def test_missing_file_exits_nonzero(runner, tmp_path):
    result = runner.invoke(health_cmd, ["check", str(tmp_path / "ghost.env")])
    assert result.exit_code == 1
    assert "ERROR" in result.output
