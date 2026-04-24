"""Resolve variable references within a .env file (e.g. VAR=${OTHER})."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass
class ResolveResult:
    resolved: Dict[str, str]
    unresolved: List[str]  # keys whose references could not be satisfied
    cycles: List[str]      # keys involved in circular references


def has_issues(result: ResolveResult) -> bool:
    return bool(result.unresolved or result.cycles)


def _parse_env(path: Path) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def _resolve_value(
    key: str,
    raw: Dict[str, str],
    resolved: Dict[str, str],
    visiting: set,
    cycles: set,
) -> str:
    if key in resolved:
        return resolved[key]
    if key in visiting:
        cycles.add(key)
        return raw.get(key, "")
    visiting.add(key)
    value = raw.get(key, "")

    def _replace(m: re.Match) -> str:
        ref = m.group(1)
        if ref not in raw:
            return m.group(0)  # leave unresolvable refs as-is
        return _resolve_value(ref, raw, resolved, visiting, cycles)

    expanded = _REF_RE.sub(_replace, value)
    visiting.discard(key)
    resolved[key] = expanded
    return expanded


def resolve_file(path: Path) -> ResolveResult:
    """Expand ${VAR} references in *path* and return a ResolveResult."""
    pairs = _parse_env(path)
    raw = {k: v for k, v in pairs}
    resolved: Dict[str, str] = {}
    cycles: set = set()

    for key in raw:
        _resolve_value(key, raw, resolved, set(), cycles)

    unresolved = [
        key
        for key, val in resolved.items()
        if _REF_RE.search(val)
    ]
    return ResolveResult(
        resolved=resolved,
        unresolved=unresolved,
        cycles=sorted(cycles),
    )
