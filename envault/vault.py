"""High-level vault operations: lock and unlock .env files."""

import os
from pathlib import Path
from envault.crypto import encrypt, decrypt

VAULT_EXTENSION = ".vault"


def lock(env_path: str, password: str, output_path: str | None = None) -> str:
    """Encrypt an .env file and write it as a .vault file."""
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    plaintext = env_file.read_text(encoding="utf-8")
    encrypted = encrypt(plaintext, password)

    out = Path(output_path) if output_path else env_file.with_suffix(VAULT_EXTENSION)
    out.write_text(encrypted, encoding="utf-8")
    return str(out)


def unlock(vault_path: str, password: str, output_path: str | None = None) -> str:
    """Decrypt a .vault file and write it as an .env file."""
    vault_file = Path(vault_path)
    if not vault_file.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    encoded = vault_file.read_text(encoding="utf-8")
    try:
        plaintext = decrypt(encoded, password)
    except Exception as exc:
        raise ValueError("Decryption failed. Wrong password or corrupted file.") from exc

    out = Path(output_path) if output_path else vault_file.with_suffix(".env")
    out.write_text(plaintext, encoding="utf-8")
    return str(out)
