"""Tests for envault.env_lint_fix."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_lint_fix import lint_fix, FixResult
from envault.cli_env_lint_fix import lint_fix_cmd


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'db_host = localhost\n'
        'API_KEY = "simplevalue"\n'
        'PORT=8080\n'
        '# a comment\n'
        '  SPACED_KEY  =  value  \n',
        encoding="utf-8",
    )
    return p


def test_lint_fix_returns_fix_result_type(env_file: Path) -> None:
    result = lint_fix(env_file)
    assert isinstance(result, FixResult)


def test_lint_fix_uppercases_lowercase_key(env_file: Path) -> None:
    result = lint_fix(env_file)
    content = env_file.read_text()
    assert "DB_HOST=" in content
    assert "db_host" not in content


def test_lint_fix_strips_whitespace_around_key(env_file: Path) -> None:
    result = lint_fix(env_file)
    content = env_file.read_text()
    assert "SPACED_KEY=value" in content


def test_lint_fix_removes_unnecessary_quotes(env_file: Path) -> None:
    result = lint_fix(env_file)
    content = env_file.read_text()
    assert 'API_KEY=simplevalue' in content
    assert '"simplevalue"' not in content


def test_lint_fix_preserves_comments(env_file: Path) -> None:
    result = lint_fix(env_file)
    content = env_file.read_text()
    assert "# a comment" in content


def test_lint_fix_fix_count_nonzero(env_file: Path) -> None:
    result = lint_fix(env_file)
    assert result.fix_count > 0


def test_lint_fix_already_clean_file(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("API_KEY=abc123\nPORT=8080\n", encoding="utf-8")
    result = lint_fix(p)
    assert result.fix_count == 0
    assert not result.changed


def test_lint_fix_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        lint_fix(tmp_path / "nonexistent.env")


def test_lint_fix_writes_file(env_file: Path) -> None:
    original = env_file.read_text()
    result = lint_fix(env_file)
    after = env_file.read_text()
    assert original != after


# --- CLI tests ---


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_run_reports_fixes(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(lint_fix_cmd, ["run", str(env_file)])
    assert result.exit_code == 0
    assert "fixed" in result.output


def test_cli_run_dry_run_does_not_write(runner: CliRunner, env_file: Path) -> None:
    original = env_file.read_text()
    result = runner.invoke(lint_fix_cmd, ["run", "--dry-run", str(env_file)])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert env_file.read_text() == original


def test_cli_run_missing_file_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(lint_fix_cmd, ["run", str(tmp_path / "missing.env")])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cli_run_clean_file_no_issues_message(runner: CliRunner, tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("KEY=value\n", encoding="utf-8")
    result = runner.invoke(lint_fix_cmd, ["run", str(p)])
    assert result.exit_code == 0
    assert "no issues" in result.output
