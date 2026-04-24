"""Tests for envault.cli_env_interpolate."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_interpolate import interpolate_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "HOST=localhost\n"
        "PORT=8080\n"
        "BASE=${HOST}:${PORT}\n"
    )
    return p


def test_show_resolves_references(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(interpolate_cmd, ["show", str(env_file)])
    assert result.exit_code == 0
    assert "BASE=localhost:8080" in result.output


def test_show_plain_key_present(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(interpolate_cmd, ["show", str(env_file)])
    assert "HOST=localhost" in result.output


def test_show_extra_context(runner: CliRunner, tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("GREETING=Hello ${NAME}\n")
    result = runner.invoke(
        interpolate_cmd, ["show", str(p), "--context", "NAME=Alice"]
    )
    assert result.exit_code == 0
    assert "GREETING=Hello Alice" in result.output


def test_show_unresolved_warning(runner: CliRunner, tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("URL=${UNDEFINED}/path\n")
    result = runner.invoke(interpolate_cmd, ["show", str(p)])
    assert result.exit_code == 0
    assert "UNDEFINED" in result.output


def test_show_strict_exits_nonzero_on_unresolved(
    runner: CliRunner, tmp_path: Path
) -> None:
    p = tmp_path / ".env"
    p.write_text("X=${MISSING}\n")
    result = runner.invoke(interpolate_cmd, ["show", str(p), "--strict"])
    assert result.exit_code != 0


def test_show_strict_exits_zero_when_all_resolved(
    runner: CliRunner, env_file: Path
) -> None:
    result = runner.invoke(interpolate_cmd, ["show", str(env_file), "--strict"])
    assert result.exit_code == 0
