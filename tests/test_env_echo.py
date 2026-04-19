"""Tests for envault.env_echo."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.vault import lock
from envault.env_echo import echo_vault, format_echo, EchoResult
from envault.cli_env_echo import echo_cmd

PASSWORD = "s3cr3t"

ENV_CONTENT = """DB_HOST=localhost
DB_PASSWORD=supersecret
APP_TOKEN=abc123
DEBUG=true
"""


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    env = tmp_path / ".env"
    env.write_text(ENV_CONTENT)
    vf = tmp_path / ".env.vault"
    lock(env, vf, PASSWORD)
    return vf


def test_echo_returns_echo_result_type(vault_file):
    result = echo_vault(vault_file, PASSWORD)
    assert isinstance(result, EchoResult)


def test_echo_all_keys_present(vault_file):
    result = echo_vault(vault_file, PASSWORD, mask=False)
    assert "DB_HOST" in result.entries
    assert "DEBUG" in result.entries
    assert result.count == 4


def test_echo_masks_sensitive_keys(vault_file):
    result = echo_vault(vault_file, PASSWORD, mask=True)
    assert result.entries["DB_PASSWORD"] == "****"
    assert result.entries["APP_TOKEN"] == "****"
    assert "DB_PASSWORD" in result.masked_keys
    assert "APP_TOKEN" in result.masked_keys


def test_echo_no_mask_shows_values(vault_file):
    result = echo_vault(vault_file, PASSWORD, mask=False)
    assert result.entries["DB_PASSWORD"] == "supersecret"
    assert result.masked_keys == []


def test_echo_filter_by_keys(vault_file):
    result = echo_vault(vault_file, PASSWORD, keys=["DEBUG"], mask=False)
    assert list(result.entries.keys()) == ["DEBUG"]


def test_echo_filter_by_prefix(vault_file):
    result = echo_vault(vault_file, PASSWORD, prefix="DB_", mask=False)
    assert all(k.startswith("DB_") for k in result.entries)
    assert "DEBUG" not in result.entries


def test_format_echo_produces_key_value_lines(vault_file):
    result = echo_vault(vault_file, PASSWORD, mask=False)
    output = format_echo(result)
    assert "DB_HOST=localhost" in output


def test_echo_wrong_password_raises(vault_file):
    with pytest.raises(Exception):
        echo_vault(vault_file, "wrongpassword")


def test_cli_show_prints_output(vault_file):
    runner = CliRunner()
    res = runner.invoke(echo_cmd, ["show", str(vault_file), "-p", PASSWORD, "--no-mask"])
    assert res.exit_code == 0
    assert "DB_HOST=localhost" in res.output


def test_cli_show_export_flag(vault_file):
    runner = CliRunner()
    res = runner.invoke(echo_cmd, ["show", str(vault_file), "-p", PASSWORD, "--no-mask", "--export"])
    assert res.exit_code == 0
    assert "export DB_HOST=localhost" in res.output


def test_cli_show_wrong_password_shows_error(vault_file):
    runner = CliRunner()
    res = runner.invoke(echo_cmd, ["show", str(vault_file), "-p", "bad"])
    assert res.exit_code != 0
    assert "Error" in res.output or "Error" in (res.stderr or "")
