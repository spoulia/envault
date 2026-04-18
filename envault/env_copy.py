"""Copy keys between vault files with optional filtering."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import lock, unlock


@dataclass
class CopyResult:
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _parse_env(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def _render_env(env: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in env.items()) + "\n"


def copy_keys(
    src: Path,
    src_password: str,
    dst: Path,
    dst_password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> CopyResult:
    """Copy keys from src vault to dst vault.

    Args:
        src: Source vault path.
        src_password: Password for source vault.
        dst: Destination vault path.
        dst_password: Password for destination vault.
        keys: Specific keys to copy; if None, copy all.
        overwrite: Whether to overwrite existing keys in dst.
    """
    src_text = unlock(src, src_password)
    src_env = _parse_env(src_text)

    if dst.exists():
        dst_text = unlock(dst, dst_password)
        dst_env = _parse_env(dst_text)
    else:
        dst_env = {}

    result = CopyResult()
    candidates = keys if keys is not None else list(src_env.keys())

    for key in candidates:
        if key not in src_env:
            result.skipped.append(key)
            continue
        if key in dst_env and not overwrite:
            result.skipped.append(key)
            continue
        dst_env[key] = src_env[key]
        result.copied.append(key)

    lock(dst, _render_env(dst_env), dst_password)
    return result
