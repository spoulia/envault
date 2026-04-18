"""Tests for envault.cli_audit commands."""

import json
import pytest
from click.testing import CliRunner
from envault.cli_audit import audit
from envault.audit import record


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def populated_log(tmp_path):
    log = str(tmp_path / "audit.json")
    record("lock", {"file": ".env"}, log_path=log)
    record("unlock", {"file": ".env"}, log_path=log)
    return log


def test_show_displays_entries(runner, populated_log):
    result = runner.invoke(audit, ["show", "--log", populated_log])
    assert result.exit_code == 0
    assert "lock" in result.output
    assert "unlock" in result.output


def test_show_last_limits_output(runner, populated_log):
    result = runner.invoke(audit, ["show", "--log", populated_log, "--last", "1"])
    assert result.exit_code == 0
    assert "unlock" in result.output
    assert result.output.count("\n") == 1


def test_show_empty_log(runner, tmp_path):
    log = str(tmp_path / "empty.json")
    result = runner.invoke(audit, ["show", "--log", log])
    assert result.exit_code == 0
    assert "No audit log entries found" in result.output


def test_clear_removes_entries(runner, populated_log):
    result = runner.invoke(audit, ["clear", "--log", populated_log], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    result2 = runner.invoke(audit, ["show", "--log", populated_log])
    assert "No audit log entries found" in result2.output


def test_export_writes_json(runner, populated_log, tmp_path):
    out = str(tmp_path / "exported.json")
    result = runner.invoke(audit, ["export", out, "--log", populated_log])
    assert result.exit_code == 0
    assert "Exported 2 entries" in result.output
    with open(out) as f:
        data = json.load(f)
    assert len(data) == 2
