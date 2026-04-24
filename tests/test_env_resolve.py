"""Tests for envault.env_resolve."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_resolve import ResolveResult, has_issues, resolve_file
from envault.cli_env_resolve import resolve_cmd


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "HOST=localhost\n"
        "PORT=5432\n"
        "DB_URL=postgres://${HOST}:${PORT}/mydb\n"
        "APP_URL=http://${HOST}/app\n"
    )
    return p


def test_resolve_returns_resolve_result_type(env_file: Path) -> None:
    result = resolve_file(env_file)
    assert isinstance(result, ResolveResult)


def test_resolve_expands_simple_reference(env_file: Path) -> None:
    result = resolve_file(env_file)
    assert result.resolved["DB_URL"] == "postgres://localhost:5432/mydb"


def test_resolve_expands_multiple_references(env_file: Path) -> None:
    result = resolve_file(env_file)
    assert result.resolved["APP_URL"] == "http://localhost/app"


def test_resolve_plain_keys_unchanged(env_file: Path) -> None:
    result = resolve_file(env_file)
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"


def test_unresolved_when_reference_missing(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("URL=http://${MISSING_HOST}/path\n")
    result = resolve_file(p)
    assert "URL" in result.unresolved


def test_has_issues_false_for_clean_file(env_file: Path) -> None:
    result = resolve_file(env_file)
    assert not has_issues(result)


def test_has_issues_true_when_unresolved(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("X=${UNDEFINED}\n")
    result = resolve_file(p)
    assert has_issues(result)


def test_cycle_detected(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("A=${B}\nB=${A}\n")
    result = resolve_file(p)
    assert result.cycles  # at least one cycle key reported


# --- CLI tests ---


def test_cli_show_prints_resolved(env_file: Path) -> None:
    runner = CliRunner()
    res = runner.invoke(resolve_cmd, ["show", str(env_file)])
    assert res.exit_code == 0
    assert "DB_URL=postgres://localhost:5432/mydb" in res.output


def test_cli_show_only_issues_clean_file(env_file: Path) -> None:
    runner = CliRunner()
    res = runner.invoke(resolve_cmd, ["show", "--only-issues", str(env_file)])
    assert res.exit_code == 0
    assert "No issues found." in res.output


def test_cli_show_only_issues_exits_nonzero(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("X=${UNDEFINED}\n")
    runner = CliRunner()
    res = runner.invoke(resolve_cmd, ["show", "--only-issues", str(p)])
    assert res.exit_code != 0
    assert "UNRESOLVED" in res.output
