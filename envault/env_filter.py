"""Filter keys from a .env file by pattern, prefix, or explicit list."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FilterResult:
    kept: dict[str, str]
    removed: dict[str, str]

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def _parse_env(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _render_env(pairs: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def filter_keys(
    path: Path,
    *,
    keys: Optional[list[str]] = None,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    exclude: bool = False,
    write: bool = False,
) -> FilterResult:
    """Filter env file keys.  By default *keeps* matching keys unless exclude=True."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    pairs = _parse_env(path.read_text())

    def matches(k: str) -> bool:
        if keys and k in keys:
            return True
        if prefix and k.startswith(prefix):
            return True
        if pattern and fnmatch.fnmatch(k, pattern):
            return True
        return False

    kept: dict[str, str] = {}
    removed: dict[str, str] = {}
    for k, v in pairs.items():
        hit = matches(k)
        keep = (not exclude and hit) or (exclude and not hit)
        if keys is None and prefix is None and pattern is None:
            keep = True
        if keep:
            kept[k] = v
        else:
            removed[k] = v

    if write:
        path.write_text(_render_env(kept))

    return FilterResult(kept=kept, removed=removed)
