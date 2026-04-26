"""Tests for envault.cli_env_mask_policy CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_env_mask_policy import mask_policy_cmd
import envault.env_mask_policy as _mod


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    policy_file = tmp_path / ".envault" / "mask_policy.json"
    monkeypatch.setattr(_mod, "_DEFAULT_POLICY_FILE", policy_file)
    return policy_file


def test_add_policy_success(runner, isolated):
    result = runner.invoke(mask_policy_cmd, ["add", "SECRET", "--action", "mask"])
    assert result.exit_code == 0
    assert "Added policy" in result.output


def test_add_policy_with_description(runner, isolated):
    result = runner.invoke(
        mask_policy_cmd,
        ["add", "TOKEN", "--action", "block", "--description", "block tokens"],
    )
    assert result.exit_code == 0


def test_add_duplicate_policy_shows_error(runner, isolated):
    runner.invoke(mask_policy_cmd, ["add", "KEY", "--action", "mask"])
    result = runner.invoke(mask_policy_cmd, ["add", "KEY", "--action", "allow"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remove_policy_success(runner, isolated):
    runner.invoke(mask_policy_cmd, ["add", "PASS", "--action", "block"])
    result = runner.invoke(mask_policy_cmd, ["remove", "PASS"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_policy_shows_error(runner, isolated):
    result = runner.invoke(mask_policy_cmd, ["remove", "GHOST"])
    assert result.exit_code != 0


def test_list_empty_policies(runner, isolated):
    result = runner.invoke(mask_policy_cmd, ["list"])
    assert result.exit_code == 0
    assert "No policies" in result.output


def test_list_shows_entries(runner, isolated):
    runner.invoke(mask_policy_cmd, ["add", "SECRET", "--action", "mask"])
    runner.invoke(mask_policy_cmd, ["add", "TOKEN", "--action", "block"])
    result = runner.invoke(mask_policy_cmd, ["list"])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "TOKEN" in result.output
