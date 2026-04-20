"""Tests for envault/cli_env_scope.py"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_scope import scope_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _reg(isolated) -> Path:
    return isolated / ".envault_scopes.json"


def test_add_scope_success(runner, isolated):
    result = runner.invoke(
        scope_cmd, ["add", "DB_URL", "prod", "--file", str(_reg(isolated))]
    )
    assert result.exit_code == 0
    assert "prod" in result.output


def test_add_invalid_scope_shows_error(runner, isolated):
    result = runner.invoke(
        scope_cmd, ["add", "KEY", "nightly", "--file", str(_reg(isolated))]
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remove_scope_success(runner, isolated):
    runner.invoke(scope_cmd, ["add", "KEY", "dev", "prod", "--file", str(_reg(isolated))])
    result = runner.invoke(
        scope_cmd, ["remove", "KEY", "dev", "--file", str(_reg(isolated))]
    )
    assert result.exit_code == 0
    assert "dev" not in result.output or "Remaining" in result.output


def test_show_scope_displays_assigned(runner, isolated):
    runner.invoke(scope_cmd, ["add", "SECRET", "staging", "--file", str(_reg(isolated))])
    result = runner.invoke(
        scope_cmd, ["show", "SECRET", "--file", str(_reg(isolated))]
    )
    assert "staging" in result.output


def test_show_scope_no_assignment_message(runner, isolated):
    result = runner.invoke(
        scope_cmd, ["show", "UNKNOWN", "--file", str(_reg(isolated))]
    )
    assert "no scopes" in result.output.lower()


def test_list_scopes_empty(runner, isolated):
    result = runner.invoke(scope_cmd, ["list", "--file", str(_reg(isolated))])
    assert "No scope" in result.output


def test_list_scopes_shows_entries(runner, isolated):
    runner.invoke(scope_cmd, ["add", "A", "dev", "--file", str(_reg(isolated))])
    runner.invoke(scope_cmd, ["add", "B", "prod", "--file", str(_reg(isolated))])
    result = runner.invoke(scope_cmd, ["list", "--file", str(_reg(isolated))])
    assert "A" in result.output
    assert "B" in result.output


def test_find_scope_returns_matching_keys(runner, isolated):
    runner.invoke(scope_cmd, ["add", "DB_URL", "prod", "--file", str(_reg(isolated))])
    runner.invoke(scope_cmd, ["add", "DEBUG", "dev", "--file", str(_reg(isolated))])
    result = runner.invoke(
        scope_cmd, ["find", "prod", "--file", str(_reg(isolated))]
    )
    assert "DB_URL" in result.output
    assert "DEBUG" not in result.output
