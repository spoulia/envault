"""Tests for envault.cli_env_audit_trail."""
from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_env_audit_trail import trail_cmd
from envault.env_audit_trail import record_change


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def trail_file(tmp_path: Path) -> Path:
    tf = tmp_path / "trail.json"
    record_change("DB_URL", None, "postgres://", "set", "prod.env", tf)
    record_change("SECRET", "old", None, "unset", "prod.env", tf)
    record_change("API_KEY", None, "xyz", "import", "dev.env", tf)
    return tf


def test_show_displays_entries(runner, trail_file):
    result = runner.invoke(trail_cmd, ["show", "--trail-file", str(trail_file)])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "SECRET" in result.output


def test_show_empty_trail(runner, tmp_path):
    tf = tmp_path / "empty.json"
    result = runner.invoke(trail_cmd, ["show", "--trail-file", str(tf)])
    assert result.exit_code == 0
    assert "No trail entries" in result.output


def test_show_filter_by_key(runner, trail_file):
    result = runner.invoke(
        trail_cmd, ["show", "--key", "API_KEY", "--trail-file", str(trail_file)]
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" not in result.output


def test_show_last_limits_output(runner, trail_file):
    result = runner.invoke(
        trail_cmd, ["show", "--last", "1", "--trail-file", str(trail_file)]
    )
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) == 1


def test_clear_removes_entries(runner, trail_file):
    result = runner.invoke(
        trail_cmd, ["clear", "--trail-file", str(trail_file)], input="y\n"
    )
    assert result.exit_code == 0
    assert "cleared" in result.output.lower()
    show = runner.invoke(trail_cmd, ["show", "--trail-file", str(trail_file)])
    assert "No trail entries" in show.output
