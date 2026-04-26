"""CLI tests for envault.cli_env_normalize."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_normalize import normalize_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'db_host = "localhost"\n'
        'api_key  =  "secret"\n',
        encoding="utf-8",
    )
    return p


def test_run_reports_changed_lines(runner: CliRunner, env_file: Path):
    result = runner.invoke(normalize_cmd, ["run", str(env_file)])
    assert result.exit_code == 0
    assert "Changed" in result.output


def test_run_writes_normalized_content(runner: CliRunner, env_file: Path):
    runner.invoke(normalize_cmd, ["run", str(env_file)])
    content = env_file.read_text(encoding="utf-8")
    assert "DB_HOST=localhost" in content
    assert "API_KEY=secret" in content


def test_run_dry_run_does_not_modify_file(runner: CliRunner, env_file: Path):
    original = env_file.read_text(encoding="utf-8")
    result = runner.invoke(normalize_cmd, ["run", "--dry-run", str(env_file)])
    assert result.exit_code == 0
    assert "Dry-run" in result.output
    assert env_file.read_text(encoding="utf-8") == original


def test_run_dry_run_shows_diff(runner: CliRunner, env_file: Path):
    result = runner.invoke(normalize_cmd, ["run", "--dry-run", str(env_file)])
    assert "-" in result.output
    assert "+" in result.output


def test_run_already_normalized_shows_no_changes(runner: CliRunner, tmp_path: Path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\n", encoding="utf-8")
    result = runner.invoke(normalize_cmd, ["run", str(p)])
    assert result.exit_code == 0
    assert "no changes" in result.output
