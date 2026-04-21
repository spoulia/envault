"""Promote keys from one environment file to another (e.g. staging -> production)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PromoteResult:
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    source: str = ""
    destination: str = ""

    @property
    def promoted_count(self) -> int:
        return len(self.promoted)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def _parse_env(path: Path) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def _render_env(pairs: Dict[str, str]) -> str:
    return "".join(f"{k}={v}\n" for k, v in pairs.items())


def promote_keys(
    src: Path,
    dst: Path,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Copy keys from *src* into *dst*.

    If *keys* is None every key from *src* is considered.
    Existing keys in *dst* are skipped unless *overwrite* is True.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    if not dst.exists():
        raise FileNotFoundError(f"Destination file not found: {dst}")

    src_pairs = _parse_env(src)
    dst_pairs = _parse_env(dst)

    candidates = keys if keys is not None else list(src_pairs.keys())

    result = PromoteResult(source=str(src), destination=str(dst))

    for key in candidates:
        if key not in src_pairs:
            result.skipped.append(key)
            continue
        if key in dst_pairs and not overwrite:
            result.skipped.append(key)
            continue
        dst_pairs[key] = src_pairs[key]
        result.promoted.append(key)

    dst.write_text(_render_env(dst_pairs))
    return result
