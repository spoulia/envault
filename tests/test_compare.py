"""Tests for envault.compare and envault.cli_compare."""
import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.vault import lock
from envault.compare import compare_vaults, format_compare, CompareResult
from envault.cli_compare import compare

PASSWORD = "testpass"


@pytest.fixture()
def vault_a(tmp_path):
    env = tmp_path / "a.env"
    env.write_text("KEY1=hello\nKEY2=world\nSHARED=same\n")
    vault = tmp_path / "a.vault"
    lock(env, vault, PASSWORD)
    return vault


@pytest.fixture()
def vault_b(tmp_path):
    env = tmp_path / "b.env"
    env.write_text("KEY3=foo\nSHARED=same\nCHANGED=new\n")
    vault = tmp_path / "b.vault"
    lock(env, vault, PASSWORD)
    return vault


@pytest.fixture()
def vault_a_with_changed(tmp_path):
    env = tmp_path / "ac.env"
    env.write_text("SHARED=different\n")
    vault = tmp_path / "ac.vault"
    lock(env, vault, PASSWORD)
    return vault


def test_compare_only_in_a(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "KEY1" in result.only_in_a
    assert "KEY2" in result.only_in_a


def test_compare_only_in_b(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "KEY3" in result.only_in_b
    assert "CHANGED" in result.only_in_b


def test_compare_same_keys(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert "SHARED" in result.same


def test_compare_different_values(vault_a, vault_a_with_changed, tmp_path):
    result = compare_vaults(vault_a, PASSWORD, vault_a_with_changed, PASSWORD)
    assert "SHARED" in result.different


def test_is_identical_false(vault_a, vault_b):
    result = compare_vaults(vault_a, PASSWORD, vault_b, PASSWORD)
    assert not result.is_identical


def test_is_identical_true(vault_a, tmp_path):
    env2 = tmp_path / "copy.env"
    env2.write_text("KEY1=hello\nKEY2=world\nSHARED=same\n")
    vault2 = tmp_path / "copy.vault"
    lock(env2, vault2, PASSWORD)
    result = compare_vaults(vault_a, PASSWORD, vault2, PASSWORD)
    assert result.is_identical


def test_format_compare_contains_labels():
    result = CompareResult(only_in_a=["X"], only_in_b=["Y"], different=["Z"], same=["W"])
    output = format_compare(result, label_a="dev", label_b="prod")
    assert "dev" in output
    assert "prod" in output
    assert "X" in output and "Y" in output


def test_cli_show_exits_1_when_different(vault_a, vault_b):
    runner = CliRunner()
    result = runner.invoke(
        compare, ["show", str(vault_a), str(vault_b), "--password-a", PASSWORD, "--password-b", PASSWORD]
    )
    assert result.exit_code == 1
    assert "KEY1" in result.output or "only in" in result.output


def test_cli_show_exits_0_when_identical(vault_a, tmp_path):
    env2 = tmp_path / "copy.env"
    env2.write_text("KEY1=hello\nKEY2=world\nSHARED=same\n")
    vault2 = tmp_path / "copy.vault"
    lock(env2, vault2, PASSWORD)
    runner = CliRunner()
    result = runner.invoke(
        compare, ["show", str(vault_a), str(vault2), "--password-a", PASSWORD, "--password-b", PASSWORD]
    )
    assert result.exit_code == 0
    assert "identical" in result.output.lower()
