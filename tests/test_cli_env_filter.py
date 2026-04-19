"""Tests for envault.cli_env_filter."""
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.cli_env_filter import filter_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAPP_SECRET=abc\nLOG_LEVEL=info\n"
    )
    return f


def test_filter_by_prefix_output(runner, env_file):
    result = runner.invoke(filter_cmd, ["run", str(env_file), "--prefix", "DB_"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "APP_SECRET" not in result.output


def test_filter_by_key_output(runner, env_file):
    result = runner.invoke(filter_cmd, ["run", str(env_file), "--key", "LOG_LEVEL"])
    assert result.exit_code == 0
    assert "LOG_LEVEL=info" in result.output
    assert "DB_HOST" not in result.output


def test_filter_exclude_flag(runner, env_file):
    result = runner.invoke(filter_cmd, ["run", str(env_file), "--prefix", "DB_", "--exclude"])
    assert result.exit_code == 0
    assert "APP_SECRET" in result.output
    assert "DB_HOST" not in result.output


def test_filter_write_flag(runner, env_file):
    result = runner.invoke(filter_cmd, ["run", str(env_file), "--prefix", "APP_", "--write"])
    assert result.exit_code == 0
    content = env_file.read_text()
    assert "APP_SECRET" in content
    assert "DB_HOST" not in content


def test_filter_missing_file_shows_error(runner, tmp_path):
    result = runner.invoke(filter_cmd, ["run", str(tmp_path / "nope.env")])
    assert result.exit_code != 0 or "Error" in result.output
