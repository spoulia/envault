"""CLI tests for env_alias commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_env_alias import alias


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env = tmp_path / ".env"
    env.write_text("API_KEY=abc123\nDB_URL=postgres://localhost/db\n")
    return tmp_path


def test_add_alias_success(runner, isolated):
    result = runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    assert result.exit_code == 0
    assert "api" in result.output
    assert "API_KEY" in result.output


def test_add_duplicate_alias_shows_error(runner, isolated):
    runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    result = runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    assert "Error" in result.output


def test_remove_alias_success(runner, isolated):
    runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    result = runner.invoke(alias, ["remove", "api", "--alias-file", "aliases.json"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_alias_shows_error(runner, isolated):
    result = runner.invoke(alias, ["remove", "ghost", "--alias-file", "aliases.json"])
    assert "Error" in result.output


def test_list_aliases_empty(runner, isolated):
    result = runner.invoke(alias, ["list", "--alias-file", "aliases.json"])
    assert "No aliases" in result.output


def test_list_aliases_shows_entries(runner, isolated):
    runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    runner.invoke(alias, ["add", "db", "DB_URL", "--alias-file", "aliases.json"])
    result = runner.invoke(alias, ["list", "--alias-file", "aliases.json"])
    assert "api" in result.output
    assert "db" in result.output


def test_resolve_shows_values(runner, isolated):
    runner.invoke(alias, ["add", "api", "API_KEY", "--alias-file", "aliases.json"])
    result = runner.invoke(alias, ["resolve", ".env", "--alias-file", "aliases.json"])
    assert "abc123" in result.output
