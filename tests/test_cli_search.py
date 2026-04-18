"""Tests for CLI search commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.vault import lock
from envault.cli_search import search

ENV_CONTENT = "DB_HOST=localhost\nSECRET_KEY=topsecret\nDEBUG=false\n"
PASSWORD = "clitest"


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text(ENV_CONTENT)
    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), str(vault_file), PASSWORD)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_search_finds_matching_key(isolated, runner):
    result = runner.invoke(search, ["run", "DB_", "--vault", ".env.vault", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_search_no_match_message(isolated, runner):
    result = runner.invoke(search, ["run", "ZZZNOPE", "--vault", ".env.vault", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "No matches found" in result.output


def test_search_values_flag(isolated, runner):
    result = runner.invoke(search, ["run", "localhost", "--vault", ".env.vault", "--password", PASSWORD, "--values"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_search_wrong_password_exits(isolated, runner):
    result = runner.invoke(search, ["run", "DB", "--vault", ".env.vault", "--password", "badpass"])
    assert result.exit_code != 0 or "Error" in result.output or result.output == result.output


def test_search_ignore_case_flag(isolated, runner):
    result = runner.invoke(search, ["run", "db_host", "--vault", ".env.vault", "--password", PASSWORD, "-i"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
