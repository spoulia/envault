"""Namespace management: prefix/strip key namespaces in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class NamespaceResult:
    affected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    output: str = ""

    @property
    def affected_count(self) -> int:
        return len(self.affected)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def _parse_env(text: str) -> List[tuple]:
    """Return list of (key, value, raw_line) preserving order."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines.append((None, None, line))
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            lines.append((k.strip(), v.strip(), line))
        else:
            lines.append((None, None, line))
    return lines


def _render_env(entries: List[tuple]) -> str:
    parts = []
    for k, v, raw in entries:
        if k is None:
            parts.append(raw)
        else:
            parts.append(f"{k}={v}")
    return "\n".join(parts)


def add_namespace(path: Path, prefix: str, overwrite: bool = False) -> NamespaceResult:
    """Prepend *prefix* to every key that does not already have it."""
    text = path.read_text()
    entries = _parse_env(text)
    result = NamespaceResult()
    new_entries = []
    for k, v, raw in entries:
        if k is None:
            new_entries.append((k, v, raw))
            continue
        if k.startswith(prefix):
            result.skipped.append(k)
            new_entries.append((k, v, raw))
        else:
            new_key = f"{prefix}{k}"
            result.affected.append(k)
            new_entries.append((new_key, v, f"{new_key}={v}"))
    result.output = _render_env(new_entries)
    path.write_text(result.output)
    return result


def strip_namespace(path: Path, prefix: str) -> NamespaceResult:
    """Remove *prefix* from every key that starts with it."""
    text = path.read_text()
    entries = _parse_env(text)
    result = NamespaceResult()
    new_entries = []
    for k, v, raw in entries:
        if k is None:
            new_entries.append((k, v, raw))
            continue
        if k.startswith(prefix):
            new_key = k[len(prefix):]
            result.affected.append(k)
            new_entries.append((new_key, v, f"{new_key}={v}"))
        else:
            result.skipped.append(k)
            new_entries.append((k, v, raw))
    result.output = _render_env(new_entries)
    path.write_text(result.output)
    return result


def list_namespaces(path: Path) -> Dict[str, List[str]]:
    """Return a mapping of detected prefix -> list of keys."""
    text = path.read_text()
    entries = _parse_env(text)
    buckets: Dict[str, List[str]] = {}
    for k, v, _ in entries:
        if k is None:
            continue
        if "_" in k:
            prefix = k.split("_")[0] + "_"
        else:
            prefix = "(none)"
        buckets.setdefault(prefix, []).append(k)
    return buckets
