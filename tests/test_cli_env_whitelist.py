"""CLI tests for envault.cli_env_whitelist."""
from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_env_whitelist import whitelist_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "APP_SECRET=s3cr3t\n"
        "DEBUG=true\n"
    )
    return p


def test_run_keeps_exact_key(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(whitelist_cmd, ["run", str(env_file), "-k", "DEBUG"])
    assert result.exit_code == 0
    assert "Kept 1" in result.output
    assert "Removed 2" in result.output


def test_run_pattern_keeps_prefix(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(whitelist_cmd, ["run", str(env_file), "-p", "DB_*"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_run_dry_run_does_not_write(runner: CliRunner, env_file: Path) -> None:
    original = env_file.read_text()
    result = runner.invoke(
        whitelist_cmd, ["run", str(env_file), "-k", "DEBUG", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "[dry-run]" in result.output
    assert env_file.read_text() == original


def test_run_no_keys_shows_error(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(whitelist_cmd, ["run", str(env_file)])
    assert result.exit_code != 0
    assert "at least one" in result.output.lower() or "Error" in result.output


def test_run_output_file(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.env"
    result = runner.invoke(
        whitelist_cmd, ["run", str(env_file), "-k", "APP_SECRET", "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "APP_SECRET" in out.read_text()
