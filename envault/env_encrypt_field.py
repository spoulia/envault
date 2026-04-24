"""Field-level encryption: encrypt/decrypt individual values in a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.crypto import derive_key, encrypt, decrypt

_MARKER = "enc:"


@dataclass
class FieldEncryptResult:
    path: str
    processed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _parse_env(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            pairs.append((k.strip(), v.strip()))
    return pairs


def _render_env(pairs: list[tuple[str, str]]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs) + "\n"


def encrypt_fields(
    path: Path,
    password: str,
    keys: list[str] | None = None,
    overwrite: bool = False,
) -> FieldEncryptResult:
    """Encrypt specific (or all) values in *path* in-place."""
    text = path.read_text()
    pairs = _parse_env(text)
    result = FieldEncryptResult(path=str(path))
    out: list[tuple[str, str]] = []
    for k, v in pairs:
        if (keys is None or k in keys):
            if v.startswith(_MARKER) and not overwrite:
                result.skipped.append(k)
                out.append((k, v))
            else:
                raw = v[len(_MARKER):] if v.startswith(_MARKER) else v
                token = encrypt(raw, password)
                out.append((k, f"{_MARKER}{token}"))
                result.processed.append(k)
        else:
            out.append((k, v))
    path.write_text(_render_env(out))
    return result


def decrypt_fields(
    path: Path,
    password: str,
    keys: list[str] | None = None,
) -> FieldEncryptResult:
    """Decrypt encrypted values in *path* in-place."""
    text = path.read_text()
    pairs = _parse_env(text)
    result = FieldEncryptResult(path=str(path))
    out: list[tuple[str, str]] = []
    for k, v in pairs:
        if (keys is None or k in keys) and v.startswith(_MARKER):
            token = v[len(_MARKER):]
            plain = decrypt(token, password)
            out.append((k, plain))
            result.processed.append(k)
        else:
            if keys and k in keys and not v.startswith(_MARKER):
                result.skipped.append(k)
            out.append((k, v))
    path.write_text(_render_env(out))
    return result
