"""Add, remove, or list inline comments on .env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CommentResult:
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    not_found: List[str] = field(default_factory=list)


def _parse_lines(path: Path) -> List[str]:
    return path.read_text().splitlines(keepends=True)


def get_comments(path: Path) -> Dict[str, str]:
    """Return a mapping of key -> comment for all keys that have inline comments."""
    result: Dict[str, str] = {}
    for line in _parse_lines(path):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, rest = stripped.partition("=")
        if "#" in rest:
            _value, _, comment = rest.partition("#")
            result[key.strip()] = comment.strip()
    return result


def set_comment(path: Path, key: str, comment: str, overwrite: bool = True) -> CommentResult:
    """Set or update an inline comment for a specific key."""
    lines = _parse_lines(path)
    result = CommentResult()
    found = False
    new_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, rest = stripped.partition("=")
            if k.strip() == key:
                found = True
                if "#" in rest and not overwrite:
                    result.skipped.append(key)
                    new_lines.append(line)
                    continue
                value = rest.partition("#")[0].rstrip()
                eol = "\n" if not line.endswith("\n") else ""
                new_lines.append(f"{k.strip()}={value}  # {comment}\n")
                result.updated.append(key)
                continue
        new_lines.append(line)
    if not found:
        result.not_found.append(key)
    path.write_text("".join(new_lines))
    return result


def remove_comment(path: Path, key: str) -> CommentResult:
    """Remove the inline comment for a specific key."""
    lines = _parse_lines(path)
    result = CommentResult()
    found = False
    new_lines: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _, rest = stripped.partition("=")
            if k.strip() == key:
                found = True
                value = rest.partition("#")[0].rstrip()
                new_lines.append(f"{k.strip()}={value}\n")
                result.updated.append(key)
                continue
        new_lines.append(line)
    if not found:
        result.not_found.append(key)
    path.write_text("".join(new_lines))
    return result
