"""env_echo.py – print resolved env vars from a vault with optional masking."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import unlock


@dataclass
class EchoResult:
    entries: Dict[str, str] = field(default_factory=dict)
    masked_keys: List[str] = field(default_factory=list)
    vault: str = ""

    @property
    def count(self) -> int:
        return len(self.entries)


_SENSITIVE = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PRIVATE", "PWD", "PASS")


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(s in upper for s in _SENSITIVE)


def echo_vault(
    vault_path: Path,
    password: str,
    *,
    keys: Optional[List[str]] = None,
    mask: bool = True,
    prefix: Optional[str] = None,
) -> EchoResult:
    """Decrypt vault and return its key/value pairs, optionally masked."""
    raw = unlock(vault_path, password)
    parsed: Dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        parsed[k.strip()] = v.strip()

    if prefix:
        parsed = {k: v for k, v in parsed.items() if k.startswith(prefix)}
    if keys:
        parsed = {k: v for k, v in parsed.items() if k in keys}

    masked_keys: List[str] = []
    entries: Dict[str, str] = {}
    for k, v in parsed.items():
        if mask and _is_sensitive(k):
            entries[k] = "****"
            masked_keys.append(k)
        else:
            entries[k] = v

    return EchoResult(entries=entries, masked_keys=masked_keys, vault=str(vault_path))


def format_echo(result: EchoResult) -> str:
    lines = [f"{k}={v}" for k, v in result.entries.items()]
    return "\n".join(lines)
