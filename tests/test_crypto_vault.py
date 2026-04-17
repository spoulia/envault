"""Tests for crypto and vault modules."""

import pytest
from pathlib import Path
from envault.crypto import encrypt, decrypt
from envault.vault import lock, unlock


SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=supersecret\n"
PASSWORD = "strongpassword123"
WRONG_PASSWORD = "wrongpassword"


# --- crypto tests ---

def test_encrypt_decrypt_roundtrip():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == SAMPLE_ENV


def test_encrypt_produces_different_ciphertexts():
    t1 = encrypt(SAMPLE_ENV, PASSWORD)
    t2 = encrypt(SAMPLE_ENV, PASSWORD)
    assert t1 != t2  # random salt/nonce


def test_decrypt_wrong_password_raises():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    with pytest.raises(Exception):
        decrypt(token, WRONG_PASSWORD)


# --- vault tests ---

def test_lock_unlock_roundtrip(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")

    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), PASSWORD, str(vault_file))
    assert vault_file.exists()

    out_env = tmp_path / ".env.decrypted"
    unlock(str(vault_file), PASSWORD, str(out_env))
    assert out_env.read_text(encoding="utf-8") == SAMPLE_ENV


def test_lock_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        lock(str(tmp_path / "nonexistent.env"), PASSWORD)


def test_unlock_wrong_password_raises(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV, encoding="utf-8")
    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), PASSWORD, str(vault_file))

    with pytest.raises(ValueError, match="Decryption failed"):
        unlock(str(vault_file), WRONG_PASSWORD)
