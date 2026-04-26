"""Normalize .env file keys and values to a canonical form."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class NormalizeResult:
    path: Path
    original_lines: List[str]
    normalized_lines: List[str]
    changes: List[Tuple[int, str, str]] = field(default_factory=list)  # (lineno, before, after)

    @property
    def changed_count(self) -> int:
        return len(self.changes)

    @property
    def changed(self) -> bool:
        return bool(self.changes)


def _normalize_key(key: str) -> str:
    """Uppercase and strip whitespace from key."""
    return key.strip().upper()


def _normalize_value(value: str) -> str:
    """Strip surrounding whitespace; remove redundant quotes if value has none inside."""
    value = value.strip()
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            inner = value[1:-1]
            if quote not in inner:
                value = inner
            break
    return value


def _normalize_line(line: str) -> str:
    """Return a normalized version of a single .env line."""
    stripped = line.rstrip("\n")
    if stripped.lstrip().startswith("#") or "=" not in stripped:
        return line
    key, _, value = stripped.partition("=")
    return f"{_normalize_key(key)}={_normalize_value(value)}\n"


def normalize_file(path: Path, *, dry_run: bool = False) -> NormalizeResult:
    """Normalize all key/value pairs in *path*.

    When *dry_run* is True the file is not modified.
    """
    raw = path.read_text(encoding="utf-8")
    original_lines = raw.splitlines(keepends=True)
    normalized_lines: List[str] = []
    changes: List[Tuple[int, str, str]] = []

    for i, line in enumerate(original_lines, start=1):
        norm = _normalize_line(line)
        normalized_lines.append(norm)
        if norm != line:
            changes.append((i, line.rstrip("\n"), norm.rstrip("\n")))

    if not dry_run and changes:
        path.write_text("".join(normalized_lines), encoding="utf-8")

    return NormalizeResult(
        path=path,
        original_lines=original_lines,
        normalized_lines=normalized_lines,
        changes=changes,
    )
