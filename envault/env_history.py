"""Track change history for .env files."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = Path(".envault_history.json")


@dataclass
class HistoryEntry:
    timestamp: float
    action: str
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    note: str = ""


@dataclass
class HistoryResult:
    entries: List[HistoryEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)


def _load(history_file: Path) -> List[dict]:
    if not history_file.exists():
        return []
    return json.loads(history_file.read_text())


def _save(data: List[dict], history_file: Path) -> None:
    history_file.write_text(json.dumps(data, indent=2))


def record_change(
    action: str,
    key: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    note: str = "",
    history_file: Path = DEFAULT_HISTORY_FILE,
) -> HistoryEntry:
    entry = HistoryEntry(
        timestamp=time.time(),
        action=action,
        key=key,
        old_value=old_value,
        new_value=new_value,
        note=note,
    )
    data = _load(history_file)
    data.append(asdict(entry))
    _save(data, history_file)
    return entry


def get_history(
    key: Optional[str] = None,
    last: Optional[int] = None,
    history_file: Path = DEFAULT_HISTORY_FILE,
) -> HistoryResult:
    raw = _load(history_file)
    entries = [HistoryEntry(**r) for r in raw]
    if key:
        entries = [e for e in entries if e.key == key]
    if last is not None:
        entries = entries[-last:]
    return HistoryResult(entries=entries)


def clear_history(history_file: Path = DEFAULT_HISTORY_FILE) -> None:
    _save([], history_file)
