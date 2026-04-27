"""env_expire.py – track expiry dates for .env keys."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_REGISTRY = Path(".envault_expiry.json")


@dataclass
class ExpiryEntry:
    key: str
    expires_on: str          # ISO-8601 date string, e.g. "2025-12-31"
    description: str = ""


@dataclass
class ExpiryResult:
    entries: List[ExpiryEntry] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.entries)


@dataclass
class ExpiredResult:
    expired: List[ExpiryEntry] = field(default_factory=list)
    upcoming: List[ExpiryEntry] = field(default_factory=list)

    @property
    def has_expired(self) -> bool:
        return bool(self.expired)


def _load(registry: Path) -> Dict[str, dict]:
    if not registry.exists():
        return {}
    return json.loads(registry.read_text())


def _save(data: Dict[str, dict], registry: Path) -> None:
    registry.write_text(json.dumps(data, indent=2))


def add_expiry(
    key: str,
    expires_on: str,
    description: str = "",
    registry: Path = DEFAULT_REGISTRY,
) -> ExpiryEntry:
    """Register an expiry date for *key*."""
    try:
        date.fromisoformat(expires_on)
    except ValueError as exc:
        raise ValueError(f"Invalid date '{expires_on}': expected YYYY-MM-DD") from exc

    data = _load(registry)
    if key in data:
        raise ValueError(f"Expiry for '{key}' already exists; remove it first.")
    data[key] = {"expires_on": expires_on, "description": description}
    _save(data, registry)
    return ExpiryEntry(key=key, expires_on=expires_on, description=description)


def remove_expiry(key: str, registry: Path = DEFAULT_REGISTRY) -> bool:
    data = _load(registry)
    if key not in data:
        return False
    del data[key]
    _save(data, registry)
    return True


def list_expiries(registry: Path = DEFAULT_REGISTRY) -> ExpiryResult:
    data = _load(registry)
    entries = [
        ExpiryEntry(key=k, expires_on=v["expires_on"], description=v.get("description", ""))
        for k, v in data.items()
    ]
    return ExpiryResult(entries=entries)


def check_expiry(
    warn_days: int = 30,
    registry: Path = DEFAULT_REGISTRY,
) -> ExpiredResult:
    """Return keys that have already expired or expire within *warn_days* days."""
    today = date.today()
    result = ExpiredResult()
    for entry in list_expiries(registry).entries:
        exp = date.fromisoformat(entry.expires_on)
        delta = (exp - today).days
        if delta < 0:
            result.expired.append(entry)
        elif delta <= warn_days:
            result.upcoming.append(entry)
    return result
