"""CLI tests for envault.cli_env_transform."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_transform import transform_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nAPP_ENV=production\n")
    return p


def test_run_uppercase_reports_changed(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(transform_cmd, ["run", str(env_file), "-o", "uppercase"])
    assert result.exit_code == 0
    assert "Changed" in result.output


def test_run_writes_file(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(transform_cmd, ["run", str(env_file), "-o", "uppercase"])
    assert "APP_ENV=PRODUCTION" in env_file.read_text()


def test_run_dry_run_does_not_write(runner: CliRunner, env_file: Path) -> None:
    original = env_file.read_text()
    runner.invoke(transform_cmd, ["run", str(env_file), "-o", "uppercase", "--dry-run"])
    assert env_file.read_text() == original


def test_run_dry_run_shows_notice(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(transform_cmd, ["run", str(env_file), "-o", "uppercase", "--dry-run"])
    assert "dry-run" in result.output


def test_run_specific_key_only(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(transform_cmd, ["run", str(env_file), "-o", "uppercase", "-k", "APP_ENV"])
    content = env_file.read_text()
    assert "APP_ENV=PRODUCTION" in content
    assert "DB_HOST=localhost" in content


def test_run_invalid_operation_shows_error(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(transform_cmd, ["run", str(env_file), "-o", "explode"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_run_missing_file_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(transform_cmd, ["run", str(tmp_path / "ghost.env"), "-o", "uppercase"])
    assert result.exit_code != 0


def test_run_replace_operation(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(
        transform_cmd,
        ["run", str(env_file), "-o", "replace:localhost:127.0.0.1"],
    )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "127.0.0.1" in env_file.read_text()
