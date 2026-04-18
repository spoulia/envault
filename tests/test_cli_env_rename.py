"""Tests for envault.cli_env_rename."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_rename import rename


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nAPI_URL=https://example.com\n")
    return f


def test_rename_success(runner: CliRunner, env_file: Path):
    result = runner.invoke(rename, ["run", str(env_file), "-m", "API_KEY=SERVICE_KEY"])
    assert result.exit_code == 0
    assert "Renamed: API_KEY -> SERVICE_KEY" in result.output
    assert "SERVICE_KEY=secret" in env_file.read_text()


def test_rename_not_found_shows_message(runner: CliRunner, env_file: Path):
    result = runner.invoke(rename, ["run", str(env_file), "-m", "GHOST=NEW"])
    assert result.exit_code == 0
    assert "Not found: GHOST" in result.output


def test_rename_skipped_shows_message(runner: CliRunner, env_file: Path):
    result = runner.invoke(rename, ["run", str(env_file), "-m", "API_KEY=API_URL"])
    assert result.exit_code == 0
    assert "Skipped" in result.output


def test_rename_writes_to_output_file(runner: CliRunner, env_file: Path, tmp_path: Path):
    dst = tmp_path / "out.env"
    result = runner.invoke(rename, ["run", str(env_file), "-m", "API_KEY=SERVICE_KEY", "-o", str(dst)])
    assert result.exit_code == 0
    assert dst.exists()
    assert "SERVICE_KEY=secret" in dst.read_text()


def test_rename_invalid_mapping_format(runner: CliRunner, env_file: Path):
    result = runner.invoke(rename, ["run", str(env_file), "-m", "BADFORMAT"])
    assert result.exit_code != 0


def test_rename_no_keys_renamed_message(runner: CliRunner, env_file: Path):
    result = runner.invoke(rename, ["run", str(env_file), "-m", "MISSING=OTHER"])
    assert "No keys were renamed" in result.output
