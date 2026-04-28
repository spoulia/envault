"""env_ownership.py – assign and query key ownership metadata."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_REGISTRY = Path(".envault_ownership.json")


@dataclass
class OwnershipEntry:
    key: str
    owner: str
    team: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class OwnershipResult:
    entries: List[OwnershipEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)

    def by_owner(self, owner: str) -> List[OwnershipEntry]:
        return [e for e in self.entries if e.owner == owner]

    def by_team(self, team: str) -> List[OwnershipEntry]:
        return [e for e in self.entries if e.team == team]


def _load_registry(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_registry(data: Dict[str, dict], path: Path) -> None:
    path.write_text(json.dumps(data, indent=2))


def assign_owner(
    key: str,
    owner: str,
    *,
    team: Optional[str] = None,
    notes: Optional[str] = None,
    registry: Path = _DEFAULT_REGISTRY,
) -> OwnershipEntry:
    data = _load_registry(registry)
    if key in data:
        raise ValueError(f"Ownership already assigned for '{key}'. Use update_owner to change it.")
    entry = {"owner": owner, "team": team, "notes": notes}
    data[key] = entry
    _save_registry(data, registry)
    return OwnershipEntry(key=key, **entry)


def update_owner(
    key: str,
    owner: str,
    *,
    team: Optional[str] = None,
    notes: Optional[str] = None,
    registry: Path = _DEFAULT_REGISTRY,
) -> OwnershipEntry:
    data = _load_registry(registry)
    entry = {"owner": owner, "team": team, "notes": notes}
    data[key] = entry
    _save_registry(data, registry)
    return OwnershipEntry(key=key, **entry)


def remove_owner(key: str, *, registry: Path = _DEFAULT_REGISTRY) -> bool:
    data = _load_registry(registry)
    if key not in data:
        return False
    del data[key]
    _save_registry(data, registry)
    return True


def get_ownership(*, registry: Path = _DEFAULT_REGISTRY) -> OwnershipResult:
    data = _load_registry(registry)
    entries = [OwnershipEntry(key=k, **v) for k, v in data.items()]
    return OwnershipResult(entries=entries)
