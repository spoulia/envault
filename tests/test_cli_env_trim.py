"""Tests for envault.cli_env_trim."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_env_trim import trim


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("X=1\nY=2\nX=3\n")
    return p


def test_trim_removes_and_reports(runner, env_file):
    result = runner.invoke(trim, ["run", str(env_file)])
    assert result.exit_code == 0
    assert "Removed duplicate: X" in result.output
    assert "Removed 1 duplicate" in result.output


def test_trim_no_duplicates_message(runner, tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\nB=2\n")
    result = runner.invoke(trim, ["run", str(p)])
    assert result.exit_code == 0
    assert "No duplicates found" in result.output


def test_trim_dry_run_shows_preview(runner, env_file):
    result = runner.invoke(trim, ["run", "--dry-run", str(env_file)])
    assert result.exit_code == 0
    assert "[dry-run]" in result.output
    assert "Would remove" in result.output
    # File should be unchanged
    assert env_file.read_text() == "X=1\nY=2\nX=3\n"


def test_trim_missing_file_shows_error(runner, tmp_path):
    result = runner.invoke(trim, ["run", str(tmp_path / "missing.env")])
    assert result.exit_code != 0
