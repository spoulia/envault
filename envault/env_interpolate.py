"""Interpolate shell-style variable references in .env files.

Supports ${VAR} and $VAR syntax, resolving values within the same file
or from an optional external context dict.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    resolved: Dict[str, str]
    unresolved: List[str]
    original: Dict[str, str]


def has_unresolved(result: InterpolateResult) -> bool:
    return bool(result.unresolved)


def _parse_env(path: Path) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip().strip('"').strip("'")
    return pairs


def _resolve_value(
    value: str,
    context: Dict[str, str],
    unresolved: List[str],
) -> str:
    def replacer(match: re.Match) -> str:  # type: ignore[type-arg]
        var = match.group(1) or match.group(2)
        if var in context:
            return context[var]
        if var not in unresolved:
            unresolved.append(var)
        return match.group(0)

    return _REF_RE.sub(replacer, value)


def interpolate_file(
    path: Path,
    extra_context: Optional[Dict[str, str]] = None,
) -> InterpolateResult:
    """Resolve variable references in *path*, returning an InterpolateResult."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    original = _parse_env(path)
    context: Dict[str, str] = {**(extra_context or {}), **original}
    unresolved: List[str] = []
    resolved: Dict[str, str] = {}

    for key, value in original.items():
        resolved[key] = _resolve_value(value, context, unresolved)

    return InterpolateResult(
        resolved=resolved,
        unresolved=sorted(set(unresolved)),
        original=original,
    )


def format_interpolate(result: InterpolateResult) -> str:
    lines: List[str] = []
    for key, value in result.resolved.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)
