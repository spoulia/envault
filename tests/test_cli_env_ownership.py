"""Tests for envault/cli_env_ownership.py"""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_env_ownership import ownership_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    reg = tmp_path / "ownership.json"
    return str(reg)


def test_assign_success(runner, isolated):
    result = runner.invoke(ownership_cmd, ["assign", "DB_PASSWORD", "alice", "--registry", isolated])
    assert result.exit_code == 0
    assert "alice" in result.output
    assert "DB_PASSWORD" in result.output


def test_assign_with_team(runner, isolated):
    result = runner.invoke(
        ownership_cmd,
        ["assign", "API_KEY", "bob", "--team", "platform", "--registry", isolated],
    )
    assert result.exit_code == 0


def test_assign_duplicate_shows_error(runner, isolated):
    runner.invoke(ownership_cmd, ["assign", "SECRET", "alice", "--registry", isolated])
    result = runner.invoke(ownership_cmd, ["assign", "SECRET", "bob", "--registry", isolated])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_update_success(runner, isolated):
    runner.invoke(ownership_cmd, ["assign", "DB_URL", "alice", "--registry", isolated])
    result = runner.invoke(ownership_cmd, ["update", "DB_URL", "carol", "--registry", isolated])
    assert result.exit_code == 0
    assert "carol" in result.output


def test_remove_success(runner, isolated):
    runner.invoke(ownership_cmd, ["assign", "OLD_KEY", "alice", "--registry", isolated])
    result = runner.invoke(ownership_cmd, ["remove", "OLD_KEY", "--registry", isolated])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_shows_message(runner, isolated):
    result = runner.invoke(ownership_cmd, ["remove", "GHOST", "--registry", isolated])
    assert result.exit_code == 0
    assert "No ownership record" in result.output


def test_list_shows_entries(runner, isolated):
    runner.invoke(ownership_cmd, ["assign", "KEY_A", "alice", "--registry", isolated])
    runner.invoke(ownership_cmd, ["assign", "KEY_B", "bob", "--registry", isolated])
    result = runner.invoke(ownership_cmd, ["list", "--registry", isolated])
    assert result.exit_code == 0
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_list_filter_by_owner(runner, isolated):
    runner.invoke(ownership_cmd, ["assign", "KEY_A", "alice", "--registry", isolated])
    runner.invoke(ownership_cmd, ["assign", "KEY_B", "bob", "--registry", isolated])
    result = runner.invoke(ownership_cmd, ["list", "--owner", "alice", "--registry", isolated])
    assert "KEY_A" in result.output
    assert "KEY_B" not in result.output


def test_list_empty_shows_message(runner, isolated):
    result = runner.invoke(ownership_cmd, ["list", "--registry", isolated])
    assert "No ownership records" in result.output
