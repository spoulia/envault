"""Tests for field-level encryption (envault/env_encrypt_field.py)."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_encrypt_field import (
    FieldEncryptResult,
    _MARKER,
    encrypt_fields,
    decrypt_fields,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=supersecret\nDEBUG=true\nDB_PASS=hunter2\n")
    return p


def test_encrypt_returns_field_encrypt_result(env_file: Path) -> None:
    result = encrypt_fields(env_file, "password")
    assert isinstance(result, FieldEncryptResult)


def test_encrypt_all_keys_processed(env_file: Path) -> None:
    result = encrypt_fields(env_file, "password")
    assert set(result.processed) == {"API_KEY", "DEBUG", "DB_PASS"}
    assert result.skipped == []


def test_encrypted_values_have_marker(env_file: Path) -> None:
    encrypt_fields(env_file, "password")
    text = env_file.read_text()
    for line in text.splitlines():
        if "=" in line:
            _, _, v = line.partition("=")
            assert v.startswith(_MARKER), f"Expected marker in: {line}"


def test_encrypt_specific_keys_only(env_file: Path) -> None:
    result = encrypt_fields(env_file, "password", keys=["API_KEY"])
    assert result.processed == ["API_KEY"]
    text = env_file.read_text()
    assert "DEBUG=true" in text


def test_encrypt_skips_already_encrypted_without_overwrite(env_file: Path) -> None:
    encrypt_fields(env_file, "password")
    result = encrypt_fields(env_file, "password")
    assert len(result.skipped) == 3
    assert result.processed == []


def test_encrypt_overwrite_re_encrypts(env_file: Path) -> None:
    encrypt_fields(env_file, "password")
    result = encrypt_fields(env_file, "password", overwrite=True)
    assert len(result.processed) == 3
    assert result.skipped == []


def test_roundtrip_encrypt_decrypt(env_file: Path) -> None:
    original = env_file.read_text()
    encrypt_fields(env_file, "mypassword")
    decrypt_fields(env_file, "mypassword")
    assert env_file.read_text() == original


def test_decrypt_wrong_password_raises(env_file: Path) -> None:
    encrypt_fields(env_file, "correct")
    with pytest.raises(Exception):
        decrypt_fields(env_file, "wrong")


def test_decrypt_skips_plain_values(env_file: Path) -> None:
    # Only API_KEY is encrypted; DEBUG and DB_PASS remain plain.
    encrypt_fields(env_file, "password", keys=["API_KEY"])
    result = decrypt_fields(env_file, "password", keys=["DEBUG", "DB_PASS"])
    assert "DEBUG" in result.skipped
    assert "DB_PASS" in result.skipped
    assert result.processed == []


def test_decrypt_specific_key(env_file: Path) -> None:
    encrypt_fields(env_file, "password")
    result = decrypt_fields(env_file, "password", keys=["API_KEY"])
    assert result.processed == ["API_KEY"]
    text = env_file.read_text()
    assert "API_KEY=supersecret" in text
    # others still encrypted
    for line in text.splitlines():
        if line.startswith("DEBUG=") or line.startswith("DB_PASS="):
            assert _MARKER in line
