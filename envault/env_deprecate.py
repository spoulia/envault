"""Mark .env keys as deprecated and warn when they are present."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEPRECATIONS_FILE = Path(".envault_deprecations.json")


@dataclass
class DeprecationEntry:
    key: str
    reason: str
    replacement: Optional[str] = None


@dataclass
class DeprecateResult:
    found: List[DeprecationEntry] = field(default_factory=list)
    clean: List[str] = field(default_factory=list)

    @property
    def has_deprecated(self) -> bool:
        return len(self.found) > 0


def _load_registry() -> Dict[str, dict]:
    if not _DEPRECATIONS_FILE.exists():
        return {}
    return json.loads(_DEPRECATIONS_FILE.read_text())


def _save_registry(registry: Dict[str, dict]) -> None:
    _DEPRECATIONS_FILE.write_text(json.dumps(registry, indent=2))


def _parse_env(path: Path) -> Dict[str, str]:
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def add_deprecation(key: str, reason: str, replacement: Optional[str] = None) -> None:
    registry = _load_registry()
    if key in registry:
        raise ValueError(f"Key '{key}' is already marked as deprecated.")
    registry[key] = {"reason": reason, "replacement": replacement}
    _save_registry(registry)


def remove_deprecation(key: str) -> None:
    registry = _load_registry()
    if key not in registry:
        raise KeyError(f"Key '{key}' is not in the deprecation registry.")
    del registry[key]
    _save_registry(registry)


def list_deprecations() -> List[DeprecationEntry]:
    registry = _load_registry()
    return [
        DeprecationEntry(key=k, reason=v["reason"], replacement=v.get("replacement"))
        for k, v in registry.items()
    ]


def scan_file(env_path: Path) -> DeprecateResult:
    registry = _load_registry()
    env = _parse_env(env_path)
    found: List[DeprecationEntry] = []
    clean: List[str] = []
    for key in env:
        if key in registry:
            found.append(
                DeprecationEntry(
                    key=key,
                    reason=registry[key]["reason"],
                    replacement=registry[key].get("replacement"),
                )
            )
        else:
            clean.append(key)
    return DeprecateResult(found=found, clean=clean)
