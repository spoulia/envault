"""Key rotation: re-encrypt vault with a new password."""

from __future__ import annotations

import json
from pathlib import Path

from envault.crypto import decrypt, encrypt
from envault.audit import record


DEFAULT_VAULT = Path(".envault")


def rotate(vault_path: Path, old_password: str, new_password: str) -> None:
    """Re-encrypt *vault_path* with *new_password*.

    Raises FileNotFoundError if the vault does not exist.
    Raises ValueError if *old_password* is incorrect.
    """
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    raw = vault_path.read_bytes()
    # decrypt raises ValueError on bad password
    plaintext = decrypt(raw, old_password)

    new_ciphertext = encrypt(plaintext, new_password)
    vault_path.write_bytes(new_ciphertext)

    record(
        "rotate",
        {"vault": str(vault_path)},
    )


def rotate_and_backup(vault_path: Path, old_password: str, new_password: str) -> Path:
    """Like *rotate* but writes a `.bak` copy of the old vault first.

    Returns the path to the backup file.
    """
    backup_path = vault_path.with_suffix(".envault.bak")
    backup_path.write_bytes(vault_path.read_bytes())

    rotate(vault_path, old_password, new_password)

    record(
        "rotate_with_backup",
        {"vault": str(vault_path), "backup": str(backup_path)},
    )
    return backup_path
