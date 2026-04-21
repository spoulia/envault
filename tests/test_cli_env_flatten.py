"""Tests for envault.cli_env_flatten."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_flatten import flatten_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'SERVER={"host": "0.0.0.0", "port": 8080}\n'
        "DEBUG=true\n"
    )
    return p


def test_run_prints_flattened_keys(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(flatten_cmd, ["run", str(env_file)])
    assert result.exit_code == 0
    assert "SERVER.host=0.0.0.0" in result.output
    assert "SERVER.port=8080" in result.output


def test_run_preserves_plain_key(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(flatten_cmd, ["run", str(env_file)])
    assert "DEBUG=true" in result.output


def test_run_writes_output_file(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "flat.env"
    result = runner.invoke(flatten_cmd, ["run", str(env_file), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "SERVER.host=0.0.0.0" in content


def test_run_quiet_suppresses_summary(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "flat.env"
    result = runner.invoke(flatten_cmd, ["run", str(env_file), "--output", str(out), "--quiet"])
    assert result.exit_code == 0
    assert "key(s)" not in result.output


def test_run_missing_file_shows_error(runner: CliRunner, tmp_path: Path) -> None:
    missing = tmp_path / "no.env"
    result = runner.invoke(flatten_cmd, ["run", str(missing)])
    assert result.exit_code != 0 or "Error" in result.output
