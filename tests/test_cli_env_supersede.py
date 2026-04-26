"""Tests for envault.cli_env_supersede."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_supersede import supersede_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_pair(tmp_path: Path):
    src = tmp_path / "source.env"
    dst = tmp_path / "target.env"
    src.write_text("DB_HOST=prod-db\nNEW_KEY=hello\n")
    dst.write_text("DB_HOST=localhost\nEXTRA=keep\n")
    return src, dst


def test_run_reports_updated_keys(runner, env_pair):
    src, dst = env_pair
    result = runner.invoke(supersede_cmd, ["run", str(src), str(dst)])
    assert result.exit_code == 0
    assert "Updated" in result.output
    assert "DB_HOST" in result.output


def test_run_reports_added_keys(runner, env_pair):
    src, dst = env_pair
    result = runner.invoke(supersede_cmd, ["run", str(src), str(dst)])
    assert result.exit_code == 0
    assert "Added" in result.output
    assert "NEW_KEY" in result.output


def test_run_writes_updated_value(runner, env_pair):
    src, dst = env_pair
    runner.invoke(supersede_cmd, ["run", str(src), str(dst)])
    assert "DB_HOST=prod-db" in dst.read_text()


def test_run_dry_run_does_not_write(runner, env_pair):
    src, dst = env_pair
    original = dst.read_text()
    result = runner.invoke(supersede_cmd, ["run", str(src), str(dst), "--dry-run"])
    assert result.exit_code == 0
    assert "[dry-run]" in result.output
    assert dst.read_text() == original


def test_run_no_overwrite_skips_existing(runner, env_pair):
    src, dst = env_pair
    result = runner.invoke(supersede_cmd, ["run", str(src), str(dst), "--no-overwrite"])
    assert result.exit_code == 0
    assert "Skipped" in result.output
    assert "DB_HOST=localhost" in dst.read_text()


def test_run_missing_source_shows_error(runner, tmp_path):
    dst = tmp_path / "target.env"
    dst.write_text("KEY=val\n")
    result = runner.invoke(supersede_cmd, ["run", str(tmp_path / "nope.env"), str(dst)])
    assert result.exit_code != 0
