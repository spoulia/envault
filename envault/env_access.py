"""env_access.py — Role-based access control for vault keys.

Allows assigning read/write/admin roles to users or teams for specific
keys or key patterns, and checking permissions before operations.
"""

from __future__ import annotations

import json
import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_REGISTRY = Path(".envault") / "access.json"
VALID_ROLES = {"read", "write", "admin"}


@dataclass
class AccessEntry:
    principal: str  # user or team name
    role: str       # read | write | admin
    pattern: str    # key pattern (glob), "*" means all keys
    note: str = ""


@dataclass
class AccessResult:
    entries: List[AccessEntry] = field(default_factory=list)
    checked_principal: Optional[str] = None
    checked_key: Optional[str] = None
    allowed: Optional[bool] = None

    @property
    def count(self) -> int:
        return len(self.entries)


def _load_registry(path: Path) -> Dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"entries": []}


def _save_registry(data: Dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def grant(
    principal: str,
    role: str,
    pattern: str = "*",
    note: str = "",
    registry: Path = DEFAULT_REGISTRY,
) -> AccessResult:
    """Grant a role to a principal for keys matching pattern."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {sorted(VALID_ROLES)}")

    data = _load_registry(registry)
    # Check for exact duplicate
    for entry in data["entries"]:
        if entry["principal"] == principal and entry["pattern"] == pattern:
            raise ValueError(
                f"Principal '{principal}' already has access for pattern '{pattern}'"
            )

    new_entry = {"principal": principal, "role": role, "pattern": pattern, "note": note}
    data["entries"].append(new_entry)
    _save_registry(data, registry)

    return AccessResult(
        entries=[AccessEntry(**e) for e in data["entries"]]
    )


def revoke(
    principal: str,
    pattern: str = "*",
    registry: Path = DEFAULT_REGISTRY,
) -> AccessResult:
    """Revoke access for a principal on a given pattern."""
    data = _load_registry(registry)
    before = len(data["entries"])
    data["entries"] = [
        e for e in data["entries"]
        if not (e["principal"] == principal and e["pattern"] == pattern)
    ]
    if len(data["entries"]) == before:
        raise KeyError(f"No access entry found for principal '{principal}' on pattern '{pattern}'")
    _save_registry(data, registry)
    return AccessResult(entries=[AccessEntry(**e) for e in data["entries"]])


def check_access(
    principal: str,
    key: str,
    required_role: str = "read",
    registry: Path = DEFAULT_REGISTRY,
) -> AccessResult:
    """Check whether a principal has the required role for a specific key."""
    role_rank = {"read": 1, "write": 2, "admin": 3}
    required_rank = role_rank.get(required_role, 0)

    data = _load_registry(registry)
    entries = [AccessEntry(**e) for e in data["entries"]]

    allowed = False
    for entry in entries:
        if entry.principal == principal and fnmatch.fnmatch(key, entry.pattern):
            if role_rank.get(entry.role, 0) >= required_rank:
                allowed = True
                break

    return AccessResult(
        entries=entries,
        checked_principal=principal,
        checked_key=key,
        allowed=allowed,
    )


def list_access(
    principal: Optional[str] = None,
    registry: Path = DEFAULT_REGISTRY,
) -> AccessResult:
    """List all access entries, optionally filtered by principal."""
    data = _load_registry(registry)
    entries = [AccessEntry(**e) for e in data["entries"]]
    if principal:
        entries = [e for e in entries if e.principal == principal]
    return AccessResult(entries=entries)
