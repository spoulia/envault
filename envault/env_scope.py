"""env_scope.py – scope/environment tagging for .env keys (dev/staging/prod)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_SCOPES = ["dev", "staging", "prod"]
_SCOPE_FILE = Path(".envault_scopes.json")


@dataclass
class ScopeResult:
    key: str
    scopes: List[str]
    all_scopes: List[str]

    @property
    def scope_count(self) -> int:
        return len(self.scopes)


def _load_registry(path: Path = _SCOPE_FILE) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_registry(registry: Dict[str, List[str]], path: Path = _SCOPE_FILE) -> None:
    path.write_text(json.dumps(registry, indent=2))


def assign_scope(key: str, scopes: List[str], path: Path = _SCOPE_FILE) -> ScopeResult:
    """Assign one or more scopes to a key."""
    for s in scopes:
        if s not in DEFAULT_SCOPES:
            raise ValueError(f"Unknown scope '{s}'. Valid: {DEFAULT_SCOPES}")
    registry = _load_registry(path)
    existing = set(registry.get(key, []))
    existing.update(scopes)
    registry[key] = sorted(existing)
    _save_registry(registry, path)
    return ScopeResult(key=key, scopes=registry[key], all_scopes=DEFAULT_SCOPES)


def remove_scope(key: str, scopes: List[str], path: Path = _SCOPE_FILE) -> ScopeResult:
    """Remove scopes from a key."""
    registry = _load_registry(path)
    existing = set(registry.get(key, []))
    existing -= set(scopes)
    registry[key] = sorted(existing)
    _save_registry(registry, path)
    return ScopeResult(key=key, scopes=registry[key], all_scopes=DEFAULT_SCOPES)


def get_scope(key: str, path: Path = _SCOPE_FILE) -> ScopeResult:
    """Get scopes assigned to a key."""
    registry = _load_registry(path)
    return ScopeResult(key=key, scopes=registry.get(key, []), all_scopes=DEFAULT_SCOPES)


def list_scopes(path: Path = _SCOPE_FILE) -> Dict[str, List[str]]:
    """Return full scope registry."""
    return _load_registry(path)


def keys_for_scope(scope: str, path: Path = _SCOPE_FILE) -> List[str]:
    """Return all keys tagged with a given scope."""
    registry = _load_registry(path)
    return sorted(k for k, scopes in registry.items() if scope in scopes)
