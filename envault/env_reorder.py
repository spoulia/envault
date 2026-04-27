"""Reorder keys in a .env file according to a specified key order list."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ReorderResult:
    source: str
    ordered_keys: List[str]
    unmatched_keys: List[str]
    lines_written: int
    output: str


def reordered_count(result: ReorderResult) -> int:
    return len(result.ordered_keys)


def unmatched_count(result: ReorderResult) -> int:
    return len(result.unmatched_keys)


def _parse_env(path: Path) -> dict:
    """Parse key=value pairs preserving insertion order."""
    pairs: dict = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        k, _, v = stripped.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def _render_env(pairs: dict) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def reorder_file(
    source: Path,
    order: List[str],
    output: Optional[Path] = None,
    append_unmatched: bool = True,
) -> ReorderResult:
    """Reorder keys in *source* according to *order*.

    Keys not listed in *order* are appended at the end when
    *append_unmatched* is True, otherwise they are dropped.
    """
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")

    pairs = _parse_env(source)
    ordered: dict = {}
    ordered_keys: List[str] = []

    for key in order:
        if key in pairs:
            ordered[key] = pairs[key]
            ordered_keys.append(key)

    unmatched: List[str] = [k for k in pairs if k not in ordered]
    if append_unmatched:
        for key in unmatched:
            ordered[key] = pairs[key]

    content = _render_env(ordered)
    dest = output or source
    dest.write_text(content)

    return ReorderResult(
        source=str(source),
        ordered_keys=ordered_keys,
        unmatched_keys=unmatched,
        lines_written=len(ordered),
        output=str(dest),
    )
