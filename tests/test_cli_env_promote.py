"""Tests for envault.cli_env_promote."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_promote import promote_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_pair(tmp_path: Path):
    src = tmp_path / ".env.staging"
    src.write_text("DB_HOST=staging-db\nDB_PORT=5432\n")
    dst = tmp_path / ".env.production"
    dst.write_text("APP_ENV=production\n")
    return src, dst


def test_promote_all_keys_success(runner: CliRunner, env_pair) -> None:
    src, dst = env_pair
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst)])
    assert result.exit_code == 0
    assert "Promoted" in result.output


def test_promote_specific_key(runner: CliRunner, env_pair) -> None:
    src, dst = env_pair
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst), "-k", "DB_PORT"])
    assert result.exit_code == 0
    assert "DB_PORT" in result.output


def test_promote_overwrite_flag(runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / ".env.staging"
    src.write_text("KEY=new_value\n")
    dst = tmp_path / ".env.production"
    dst.write_text("KEY=old_value\n")
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst), "--overwrite"])
    assert result.exit_code == 0
    assert "KEY=new_value" in dst.read_text()


def test_promote_missing_dst_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / ".env.staging"
    src.write_text("KEY=val\n")
    dst = tmp_path / "nonexistent.env"
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst)])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_promote_skipped_keys_reported(runner: CliRunner, env_pair) -> None:
    src, dst = env_pair
    # Add same key to dst so it gets skipped
    dst.write_text("DB_HOST=prod-db\n")
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst), "-k", "DB_HOST"])
    assert result.exit_code == 0
    assert "Skipped" in result.output


def test_promote_no_keys_promoted_message(runner: CliRunner, tmp_path: Path) -> None:
    src = tmp_path / "src.env"
    src.write_text("KEY=val\n")
    dst = tmp_path / "dst.env"
    dst.write_text("KEY=other\n")
    result = runner.invoke(promote_cmd, ["run", str(src), str(dst)])
    assert result.exit_code == 0
    assert "No keys were promoted" in result.output
