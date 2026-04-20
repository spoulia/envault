"""Tests for envault.env_deprecate."""
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.env_deprecate import (
    add_deprecation,
    remove_deprecation,
    list_deprecations,
    scan_file,
    DeprecateResult,
    DeprecationEntry,
    _DEPRECATIONS_FILE,
)
from envault.cli_env_deprecate import deprecate_cmd


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def env_file(isolated):
    p = isolated / ".env"
    p.write_text("OLD_KEY=value1\nNEW_KEY=value2\nANOTHER=val\n")
    return p


def test_add_deprecation_creates_entry():
    add_deprecation("OLD_KEY", "No longer used", replacement="NEW_KEY")
    entries = list_deprecations()
    assert any(e.key == "OLD_KEY" for e in entries)


def test_add_deprecation_persists():
    add_deprecation("LEGACY", "Replaced", replacement="MODERN")
    assert _DEPRECATIONS_FILE.exists()
    entries = list_deprecations()
    entry = next(e for e in entries if e.key == "LEGACY")
    assert entry.reason == "Replaced"
    assert entry.replacement == "MODERN"


def test_add_duplicate_raises():
    add_deprecation("DUP_KEY", "First")
    with pytest.raises(ValueError, match="already marked"):
        add_deprecation("DUP_KEY", "Second")


def test_remove_deprecation():
    add_deprecation("REMOVE_ME", "Gone")
    remove_deprecation("REMOVE_ME")
    entries = list_deprecations()
    assert all(e.key != "REMOVE_ME" for e in entries)


def test_remove_nonexistent_raises():
    with pytest.raises(KeyError):
        remove_deprecation("GHOST_KEY")


def test_scan_file_finds_deprecated(env_file):
    add_deprecation("OLD_KEY", "Outdated", replacement="NEW_KEY")
    result = scan_file(env_file)
    assert isinstance(result, DeprecateResult)
    assert result.has_deprecated
    keys = [e.key for e in result.found]
    assert "OLD_KEY" in keys


def test_scan_file_clean_keys(env_file):
    add_deprecation("OLD_KEY", "Outdated")
    result = scan_file(env_file)
    assert "NEW_KEY" in result.clean
    assert "ANOTHER" in result.clean


def test_scan_file_no_deprecated(env_file):
    result = scan_file(env_file)
    assert not result.has_deprecated
    assert len(result.clean) == 3


def test_cli_add_and_list():
    runner = CliRunner()
    result = runner.invoke(deprecate_cmd, ["add", "OLD", "--reason", "Obsolete", "--replacement", "NEW"])
    assert result.exit_code == 0
    assert "OLD" in result.output

    result = runner.invoke(deprecate_cmd, ["list"])
    assert "OLD" in result.output
    assert "Obsolete" in result.output
    assert "NEW" in result.output


def test_cli_scan_reports_deprecated(env_file):
    runner = CliRunner()
    runner.invoke(deprecate_cmd, ["add", "OLD_KEY", "--reason", "Replaced"])
    result = runner.invoke(deprecate_cmd, ["scan", str(env_file)])
    assert result.exit_code == 0
    assert "DEPRECATED" in result.output
    assert "OLD_KEY" in result.output


def test_cli_scan_clean_file(env_file):
    runner = CliRunner()
    result = runner.invoke(deprecate_cmd, ["scan", str(env_file)])
    assert result.exit_code == 0
    assert "No deprecated" in result.output
