"""env_whitelist.py – filter an env file to only allowed keys."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class WhitelistResult:
    kept: List[str]
    removed: List[str]
    output: str  # rendered .env text

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def _parse_env(text: str) -> List[tuple]:
    """Return list of (key, raw_line) for non-comment, non-blank lines."""
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            pairs.append((key, line))
    return pairs


def _render_env(lines: List[str]) -> str:
    return "\n".join(lines) + ("\n" if lines else "")


def whitelist_file(
    src: Path,
    allowed: List[str],
    *,
    patterns: Optional[List[str]] = None,
    output: Optional[Path] = None,
) -> WhitelistResult:
    """Keep only keys present in *allowed* or matching any glob *patterns*."""
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    compiled = [re.compile(fnmatch_to_re(p)) for p in (patterns or [])]
    text = src.read_text()
    pairs = _parse_env(text)

    kept_lines, kept_keys, removed_keys = [], [], []
    for key, line in pairs:
        if key in allowed or any(rx.match(key) for rx in compiled):
            kept_lines.append(line)
            kept_keys.append(key)
        else:
            removed_keys.append(key)

    rendered = _render_env(kept_lines)
    dest = output or src
    dest.write_text(rendered)
    return WhitelistResult(kept=kept_keys, removed=removed_keys, output=rendered)


def fnmatch_to_re(pattern: str) -> str:
    """Convert a simple glob pattern (only * wildcard) to a regex string."""
    escaped = re.escape(pattern).replace(r"\*", ".*")
    return f"^{escaped}$"
