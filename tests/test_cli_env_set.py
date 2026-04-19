import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.vault import lock
from envault.cli_env_set import envset

PASSWORD = "testpass"


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(isolated):
    vf = isolated / "test.vault"
    lock(vf, "KEY1=value1\nKEY2=value2\n", PASSWORD)
    return vf


def test_set_key_success(runner, vault_file):
    result = runner.invoke(envset, ["set", str(vault_file), "KEY3=value3", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "set: KEY3" in result.output


def test_set_no_overwrite_shows_skipped(runner, vault_file):
    result = runner.invoke(envset, ["set", str(vault_file), "KEY1=new", "--password", PASSWORD, "--no-overwrite"])
    assert result.exit_code == 0
    assert "skipped" in result.output


def test_unset_key_success(runner, vault_file):
    result = runner.invoke(envset, ["unset", str(vault_file), "KEY1", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "unset: KEY1" in result.output


def test_unset_missing_key_shows_not_found(runner, vault_file):
    result = runner.invoke(envset, ["unset", str(vault_file), "GHOST", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "not found: GHOST" in result.output


def test_list_keys_no_values(runner, vault_file):
    result = runner.invoke(envset, ["list", str(vault_file), "--password", PASSWORD])
    assert result.exit_code == 0
    assert "KEY1" in result.output
    assert "value1" not in result.output


def test_list_keys_with_values(runner, vault_file):
    result = runner.invoke(envset, ["list", str(vault_file), "--password", PASSWORD, "--show-values"])
    assert result.exit_code == 0
    assert "KEY1=value1" in result.output
