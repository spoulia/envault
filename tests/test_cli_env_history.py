"""Tests for envault.cli_env_history."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_env_history import history
from envault.env_history import record_change


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def hfile(tmp_path):
    return tmp_path / "history.json"


def test_show_empty_history(runner, hfile):
    result = runner.invoke(history, ["show", "--file", str(hfile)])
    assert result.exit_code == 0
    assert "No history entries found" in result.output


def test_show_displays_entries(runner, hfile):
    record_change("set", "API_KEY", old_value=None, new_value="secret", history_file=hfile)
    result = runner.invoke(history, ["show", "--file", str(hfile)])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "secret" in result.output


def test_show_filter_by_key(runner, hfile):
    record_change("set", "A", new_value="1", history_file=hfile)
    record_change("set", "B", new_value="2", history_file=hfile)
    result = runner.invoke(history, ["show", "--key", "A", "--file", str(hfile)])
    assert "A" in result.output
    assert "B" not in result.output


def test_show_last_limits_output(runner, hfile):
    for i in range(4):
        record_change("set", f"K{i}", new_value=str(i), history_file=hfile)
    result = runner.invoke(history, ["show", "--last", "2", "--file", str(hfile)])
    assert "K3" in result.output
    assert "K0" not in result.output


def test_clear_history(runner, hfile):
    record_change("set", "X", new_value="1", history_file=hfile)
    result = runner.invoke(history, ["clear", "--file", str(hfile)], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    check = runner.invoke(history, ["show", "--file", str(hfile)])
    assert "No history entries found" in check.output
