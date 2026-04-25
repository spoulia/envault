"""env_blacklist: remove or redact keys matching a blacklist from .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class BlacklistResult:
    removed: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)
    output: str = ""


def removed_count(result: BlacklistResult) -> int:
    return len(result.removed)


def kept_count(result: BlacklistResult) -> int:
    return len(result.kept)


def _parse_env(text: str) -> List[tuple]:
    """Return list of (key, raw_line) pairs, preserving comments/blanks as (None, line)."""
    lines = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines.append((None, line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            lines.append((key, line))
        else:
            lines.append((None, line))
    return lines


def _render_env(pairs: List[tuple]) -> str:
    return "".join(raw for _, raw in pairs)


def _matches(key: str, keys: List[str], patterns: List[str]) -> bool:
    if key in keys:
        return True
    for pat in patterns:
        if re.search(pat, key):
            return True
    return False


def blacklist_file(
    path: Path,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    dry_run: bool = False,
) -> BlacklistResult:
    """Remove keys matching *keys* list or *patterns* regexes from *path*."""
    keys = keys or []
    patterns = patterns or []
    text = path.read_text()
    pairs = _parse_env(text)
    result = BlacklistResult()
    kept_pairs: List[tuple] = []
    for key, raw in pairs:
        if key is None:
            kept_pairs.append((key, raw))
        elif _matches(key, keys, patterns):
            result.removed.append(key)
        else:
            result.kept.append(key)
            kept_pairs.append((key, raw))
    result.output = _render_env(kept_pairs)
    if not dry_run:
        path.write_text(result.output)
    return result
