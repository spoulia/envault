"""env_diff_summary.py – produce a human-readable summary of changes between
two .env files, suitable for commit messages or PR descriptions."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DiffSummaryResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def total_added(self) -> int:
        return len(self.added)

    @property
    def total_removed(self) -> int:
        return len(self.removed)

    @property
    def total_changed(self) -> int:
        return len(self.changed)


def _parse_env(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def summarise(before: Path, after: Path) -> DiffSummaryResult:
    """Compare two .env files and return a structured DiffSummaryResult."""
    if not before.exists():
        raise FileNotFoundError(f"File not found: {before}")
    if not after.exists():
        raise FileNotFoundError(f"File not found: {after}")

    old = _parse_env(before)
    new = _parse_env(after)

    result = DiffSummaryResult()
    all_keys = set(old) | set(new)

    for key in all_keys:
        if key in old and key not in new:
            result.removed[key] = old[key]
        elif key not in old and key in new:
            result.added[key] = new[key]
        elif old[key] != new[key]:
            result.changed[key] = (old[key], new[key])
        else:
            result.unchanged[key] = old[key]

    return result


def format_summary(result: DiffSummaryResult, mask_values: bool = True) -> str:
    """Return a printable summary string."""
    lines: List[str] = []

    def _val(v: str) -> str:
        return "***" if mask_values else v

    if not result.has_changes:
        return "No changes detected."

    if result.added:
        lines.append(f"Added ({result.total_added}):")
        for k, v in sorted(result.added.items()):
            lines.append(f"  + {k}={_val(v)}")

    if result.removed:
        lines.append(f"Removed ({result.total_removed}):")
        for k, v in sorted(result.removed.items()):
            lines.append(f"  - {k}={_val(v)}")

    if result.changed:
        lines.append(f"Changed ({result.total_changed}):")
        for k, (old_v, new_v) in sorted(result.changed.items()):
            lines.append(f"  ~ {k}: {_val(old_v)} -> {_val(new_v)}")

    return "\n".join(lines)
