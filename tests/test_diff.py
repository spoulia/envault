"""Tests for envault.diff and cli_diff."""
import json
import pytest
from click.testing import CliRunner
from envault.vault import lock
from envault.diff import diff_vaults, format_diff, DiffResult
from envault.cli_diff import diff


ENV_A = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n"
ENV_B = "DB_HOST=remotehost\nDB_PORT=5432\nNEW_KEY=xyz\n"


@pytest.fixture()
def vault_a(tmp_path):
    p = tmp_path / "a.vault"
    lock(str(p), ENV_A, "passA")
    return str(p)


@pytest.fixture()
def vault_b(tmp_path):
    p = tmp_path / "b.vault"
    lock(str(p), ENV_B, "passB")
    return str(p)


def test_diff_detects_added(vault_a, vault_b):
    result = diff_vaults(vault_a, "passA", vault_b, "passB")
    assert "NEW_KEY" in result.added
    assert result.added["NEW_KEY"] == "xyz"


def test_diff_detects_removed(vault_a, vault_b):
    result = diff_vaults(vault_a, "passA", vault_b, "passB")
    assert "SECRET" in result.removed


def test_diff_detects_changed(vault_a, vault_b):
    result = diff_vaults(vault_a, "passA", vault_b, "passB")
    assert "DB_HOST" in result.changed
    assert result.changed["DB_HOST"] == ("localhost", "remotehost")


def test_diff_unchanged_key_not_in_changed(vault_a, vault_b):
    result = diff_vaults(vault_a, "passA", vault_b, "passB")
    assert "DB_PORT" not in result.changed


def test_format_diff_no_differences(tmp_path):
    result = DiffResult(added={}, removed={}, changed={})
    assert format_diff(result) == "(no differences)"


def test_format_diff_shows_symbols(vault_a, vault_b):
    result = diff_vaults(vault_a, "passA", vault_b, "passB")
    text = format_diff(result)
    assert "+" in text
    assert "-" in text
    assert "~" in text


def test_wrong_password_raises(vault_a, vault_b):
    with pytest.raises(ValueError):
        diff_vaults(vault_a, "wrong", vault_b, "passB")


def test_cli_show(vault_a, vault_b):
    runner = CliRunner()
    result = runner.invoke(
        diff, ["show", vault_a, vault_b, "--password-a", "passA", "--password-b", "passB"]
    )
    assert result.exit_code == 0
    assert "+" in result.output or "-" in result.output


def test_cli_summary(vault_a, vault_b):
    runner = CliRunner()
    result = runner.invoke(
        diff, ["show", vault_a, vault_b, "--password-a", "passA", "--password-b", "passB", "--summary"]
    )
    assert result.exit_code == 0
    assert "Added:" in result.output
    assert "Removed:" in result.output
