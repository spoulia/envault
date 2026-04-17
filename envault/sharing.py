"""Sharing module: export/import encrypted vault bundles for team sharing."""

import json
import base64
import os
from pathlib import Path
from envault.crypto import encrypt, decrypt


BUNDLE_VERSION = 1


def export_bundle(vault_path: str, password: str, recipient_hint: str = "") -> str:
    """Read a locked vault file and wrap it in a shareable JSON bundle."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_path}")

    raw = vault_path.read_bytes()
    # Re-encrypt the raw ciphertext bytes under the same password so the
    # bundle carries its own independent encryption layer.
    bundle_ciphertext = encrypt(raw, password)

    bundle = {
        "version": BUNDLE_VERSION,
        "recipient": recipient_hint,
        "data": base64.b64encode(bundle_ciphertext).decode(),
    }
    return json.dumps(bundle, indent=2)


def import_bundle(bundle_json: str, password: str, output_path: str) -> None:
    """Decode a bundle and write the inner vault file to *output_path*."""
    try:
        bundle = json.loads(bundle_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid bundle format: {exc}") from exc

    if bundle.get("version") != BUNDLE_VERSION:
        raise ValueError(f"Unsupported bundle version: {bundle.get('version')}")

    raw_ciphertext = base64.b64decode(bundle["data"])
    inner = decrypt(raw_ciphertext, password)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(inner)
