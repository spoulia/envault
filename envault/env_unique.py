"""Check and enforce unique values across .env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class UniqueResult:
    duplicates: Dict[str, List[str]]  # value -> list of keys sharing it
    total_keys: int
    unique_values: int

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)


def _parse_env(path: Path) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def find_duplicate_values(path: Path) -> UniqueResult:
    """Find keys that share the same value."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    pairs = _parse_env(path)
    value_map: Dict[str, List[str]] = {}
    for key, value in pairs:
        value_map.setdefault(value, []).append(key)

    duplicates = {v: keys for v, keys in value_map.items() if len(keys) > 1}
    return UniqueResult(
        duplicates=duplicates,
        total_keys=len(pairs),
        unique_values=len(value_map),
    )


def format_unique(result: UniqueResult) -> str:
    if not result.has_duplicates:
        return "All values are unique."
    lines = ["Duplicate values found:"]
    for value, keys in result.duplicates.items():
        display = value if len(value) <= 30 else value[:27] + "..."
        lines.append(f"  {display!r}: {', '.join(keys)}")
    return "\n".join(lines)
