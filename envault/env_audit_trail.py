"""env_audit_trail.py – per-key change trail for .env files."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_DEFAULT_TRAIL = Path(".envault") / "audit_trail.json"


@dataclass
class TrailEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    action: str          # "set" | "unset" | "rename" | "import"
    source: str          # filename that changed
    timestamp: float = field(default_factory=time.time)


@dataclass
class TrailResult:
    entries: List[TrailEntry]

    @property
    def count(self) -> int:
        return len(self.entries)


def _load(trail_file: Path) -> List[dict]:
    if not trail_file.exists():
        return []
    return json.loads(trail_file.read_text())


def _save(data: List[dict], trail_file: Path) -> None:
    trail_file.parent.mkdir(parents=True, exist_ok=True)
    trail_file.write_text(json.dumps(data, indent=2))


def record_change(
    key: str,
    old_value: Optional[str],
    new_value: Optional[str],
    action: str,
    source: str,
    trail_file: Path = _DEFAULT_TRAIL,
) -> TrailEntry:
    """Append one change entry to the audit trail."""
    if action not in {"set", "unset", "rename", "import"}:
        raise ValueError(f"Unknown action: {action!r}")
    entry = TrailEntry(
        key=key,
        old_value=old_value,
        new_value=new_value,
        action=action,
        source=source,
    )
    data = _load(trail_file)
    data.append(entry.__dict__)
    _save(data, trail_file)
    return entry


def get_trail(
    key: Optional[str] = None,
    source: Optional[str] = None,
    trail_file: Path = _DEFAULT_TRAIL,
) -> TrailResult:
    """Return trail entries, optionally filtered by key or source file."""
    raw = _load(trail_file)
    entries = [TrailEntry(**r) for r in raw]
    if key:
        entries = [e for e in entries if e.key == key]
    if source:
        entries = [e for e in entries if e.source == source]
    return TrailResult(entries=entries)


def clear_trail(trail_file: Path = _DEFAULT_TRAIL) -> None:
    """Remove all entries from the audit trail."""
    if trail_file.exists():
        trail_file.unlink()
