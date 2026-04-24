"""CLI tests for field-level encryption commands."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_encrypt_field import field_encrypt_cmd
from envault.env_encrypt_field import _MARKER


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner(mix_stderr=False)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=topsecret\nDEBUG=false\n")
    return p


def test_encrypt_success(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(
        field_encrypt_cmd,
        ["encrypt", str(env_file), "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "Encrypted 2 key(s)" in result.output


def test_encrypt_specific_key(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(
        field_encrypt_cmd,
        ["encrypt", str(env_file), "--password", "pass", "--key", "API_KEY"],
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    text = env_file.read_text()
    assert "DEBUG=false" in text


def test_encrypt_skip_already_encrypted(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(field_encrypt_cmd, ["encrypt", str(env_file), "--password", "pass"])
    result = runner.invoke(
        field_encrypt_cmd,
        ["encrypt", str(env_file), "--password", "pass"],
    )
    assert "Skipped" in result.output


def test_decrypt_success(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(field_encrypt_cmd, ["encrypt", str(env_file), "--password", "pass"])
    result = runner.invoke(
        field_encrypt_cmd,
        ["decrypt", str(env_file), "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "Decrypted 2 key(s)" in result.output
    text = env_file.read_text()
    assert _MARKER not in text


def test_decrypt_wrong_password_shows_error(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(field_encrypt_cmd, ["encrypt", str(env_file), "--password", "correct"])
    result = runner.invoke(
        field_encrypt_cmd,
        ["decrypt", str(env_file), "--password", "wrong"],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_encrypt_overwrite_flag(runner: CliRunner, env_file: Path) -> None:
    runner.invoke(field_encrypt_cmd, ["encrypt", str(env_file), "--password", "pass"])
    result = runner.invoke(
        field_encrypt_cmd,
        ["encrypt", str(env_file), "--password", "pass", "--overwrite"],
    )
    assert result.exit_code == 0
    assert "Encrypted" in result.output
