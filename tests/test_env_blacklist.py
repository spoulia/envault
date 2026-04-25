"""Tests for envault.env_blacklist."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_blacklist import (
    BlacklistResult,
    blacklist_file,
    kept_count,
    removed_count,
)
from envault.cli_env_blacklist import blacklist_cmd


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "API_KEY=secret\n"
        "DB_PASSWORD=hunter2\n"
        "APP_NAME=myapp\n"
        "DEBUG=true\n"
    )
    return p


def test_blacklist_returns_blacklist_result_type(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["API_KEY"])
    assert isinstance(result, BlacklistResult)


def test_blacklist_removes_exact_key(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["API_KEY"])
    assert "API_KEY" in result.removed
    assert "API_KEY" not in result.kept


def test_blacklist_keeps_other_keys(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["API_KEY"])
    assert "APP_NAME" in result.kept
    assert "DEBUG" in result.kept


def test_blacklist_writes_file(env_file: Path) -> None:
    blacklist_file(env_file, keys=["API_KEY"])
    content = env_file.read_text()
    assert "API_KEY" not in content
    assert "APP_NAME" in content


def test_blacklist_pattern_removes_matching_keys(env_file: Path) -> None:
    result = blacklist_file(env_file, patterns=[r"PASSWORD$"])
    assert "DB_PASSWORD" in result.removed
    assert "API_KEY" in result.kept


def test_blacklist_dry_run_does_not_write(env_file: Path) -> None:
    original = env_file.read_text()
    result = blacklist_file(env_file, keys=["API_KEY"], dry_run=True)
    assert env_file.read_text() == original
    assert "API_KEY" in result.removed


def test_removed_count_helper(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["API_KEY", "DB_PASSWORD"])
    assert removed_count(result) == 2


def test_kept_count_helper(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["API_KEY"])
    assert kept_count(result) == 3


def test_no_match_removes_nothing(env_file: Path) -> None:
    result = blacklist_file(env_file, keys=["NONEXISTENT"])
    assert removed_count(result) == 0
    assert kept_count(result) == 4


# --- CLI tests ---


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_run_removes_key(runner: CliRunner, env_file: Path) -> None:
    r = runner.invoke(blacklist_cmd, ["run", str(env_file), "-k", "API_KEY"])
    assert r.exit_code == 0
    assert "Removed" in r.output
    assert "API_KEY" not in env_file.read_text()


def test_cli_run_dry_run_shows_preview(runner: CliRunner, env_file: Path) -> None:
    original = env_file.read_text()
    r = runner.invoke(blacklist_cmd, ["run", str(env_file), "-k", "API_KEY", "--dry-run"])
    assert r.exit_code == 0
    assert "dry-run" in r.output
    assert env_file.read_text() == original


def test_cli_run_no_key_or_pattern_shows_error(runner: CliRunner, env_file: Path) -> None:
    r = runner.invoke(blacklist_cmd, ["run", str(env_file)])
    assert r.exit_code != 0
