"""Trim unused/duplicate keys from .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class TrimResult:
    removed: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)
    original_path: str = ""

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def kept_count(self) -> int:
        return len(self.kept)


def _parse_env(text: str) -> list[tuple[str, str, str]]:
    """Return list of (key, value, raw_line) preserving comments/blanks."""
    entries = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            entries.append(("", "", line))
            continue
        if "=" in stripped:
            key, _, val = stripped.partition("=")
            entries.append((key.strip(), val.strip(), line))
        else:
            entries.append(("", "", line))
    return entries


def _render_env(entries: list[tuple[str, str, str]]) -> str:
    return "\n".join(line for _, _, line in entries) + "\n"


def trim_file(path: Path, *, dry_run: bool = False) -> TrimResult:
    """Remove duplicate keys, keeping the last occurrence."""
    text = path.read_text()
    entries = _parse_env(text)

    seen: dict[str, int] = {}
    for idx, (key, _, _) in enumerate(entries):
        if key:
            seen[key] = idx

    result = TrimResult(original_path=str(path))
    kept_entries = []
    for idx, (key, val, raw) in enumerate(entries):
        if key and seen[key] != idx:
            result.removed.append(key)
        else:
            if key:
                result.kept.append(key)
            kept_entries.append((key, val, raw))

    if not dry_run and result.removed_count > 0:
        path.write_text(_render_env(kept_entries))

    return result
