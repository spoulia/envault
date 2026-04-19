"""Set, unset, and list keys in a decrypted .env vault."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from envault.vault import lock, unlock


@dataclass
class SetResult:
    set: list[str] = field(default_factory=list)
    unset: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def _parse_env(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            pairs[k.strip()] = v.strip()
    return pairs


def _render_env(pairs: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def set_keys(
    vault_path: Path,
    password: str,
    updates: dict[str, str],
    overwrite: bool = True,
) -> SetResult:
    """Set one or more keys in the vault."""
    plain = unlock(vault_path, password)
    pairs = _parse_env(plain)
    result = SetResult()
    for k, v in updates.items():
        if k in pairs and not overwrite:
            result.skipped.append(k)
        else:
            pairs[k] = v
            result.set.append(k)
    lock(vault_path, _render_env(pairs), password)
    return result


def unset_keys(vault_path: Path, password: str, keys: list[str]) -> SetResult:
    """Remove one or more keys from the vault."""
    plain = unlock(vault_path, password)
    pairs = _parse_env(plain)
    result = SetResult()
    for k in keys:
        if k in pairs:
            del pairs[k]
            result.unset.append(k)
        else:
            result.skipped.append(k)
    lock(vault_path, _render_env(pairs), password)
    return result


def list_keys(vault_path: Path, password: str) -> dict[str, str]:
    """Return all key/value pairs from the vault."""
    plain = unlock(vault_path, password)
    return _parse_env(plain)
