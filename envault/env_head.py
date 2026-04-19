"""env_head.py – show the first N keys from a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class HeadResult:
    lines: List[Tuple[str, str]] = field(default_factory=list)
    total_keys: int = 0
    shown: int = 0


def _parse_env(path: Path) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def head_file(path: Path, n: int = 10) -> HeadResult:
    """Return the first *n* key/value pairs from *path*."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if n < 1:
        raise ValueError("n must be >= 1")

    all_pairs = _parse_env(path)
    selected = all_pairs[:n]
    return HeadResult(lines=selected, total_keys=len(all_pairs), shown=len(selected))


def format_head(result: HeadResult) -> str:
    """Format a HeadResult for terminal display."""
    if not result.lines:
        return "(no keys)"
    rows = [f"{k}={v}" for k, v in result.lines]
    if result.total_keys > result.shown:
        rows.append(f"... ({result.total_keys - result.shown} more key(s) not shown)")
    return "\n".join(rows)
