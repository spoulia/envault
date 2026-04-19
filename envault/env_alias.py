"""env_alias: create and resolve key aliases in .env files."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_ALIAS_FILE = Path(".envault_aliases.json")


@dataclass
class AliasResult:
    alias: str
    target: str
    resolved_value: Optional[str] = None


def _load_aliases(alias_file: Path = _ALIAS_FILE) -> Dict[str, str]:
    if not alias_file.exists():
        return {}
    return json.loads(alias_file.read_text())


def _save_aliases(aliases: Dict[str, str], alias_file: Path = _ALIAS_FILE) -> None:
    alias_file.write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, target: str, alias_file: Path = _ALIAS_FILE) -> None:
    """Register 'alias' as a synonym for 'target'."""
    aliases = _load_aliases(alias_file)
    if alias in aliases:
        raise ValueError(f"Alias '{alias}' already exists (points to '{aliases[alias]}').")
    aliases[alias] = target
    _save_aliases(aliases, alias_file)


def remove_alias(alias: str, alias_file: Path = _ALIAS_FILE) -> None:
    aliases = _load_aliases(alias_file)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(aliases, alias_file)


def list_aliases(alias_file: Path = _ALIAS_FILE) -> Dict[str, str]:
    return _load_aliases(alias_file)


def resolve_aliases(env_file: Path, alias_file: Path = _ALIAS_FILE) -> List[AliasResult]:
    """Return resolved values for all registered aliases from the given env file."""
    aliases = _load_aliases(alias_file)
    env: Dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")

    results = []
    for alias, target in aliases.items():
        results.append(AliasResult(alias=alias, target=target, resolved_value=env.get(target)))
    return results
