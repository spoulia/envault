"""Apply a diff patch to an .env file — add, change, or remove keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ApplyResult:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _parse_env(text: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def _render_env(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def apply_patch(
    target: Path,
    *,
    add: Optional[Dict[str, str]] = None,
    update: Optional[Dict[str, str]] = None,
    remove: Optional[List[str]] = None,
    overwrite: bool = True,
) -> ApplyResult:
    """Apply a patch (add/update/remove) to an env file in-place."""
    if not target.exists():
        raise FileNotFoundError(f"{target} not found")

    pairs = _parse_env(target.read_text())
    result = ApplyResult()

    for k, v in (add or {}).items():
        if k in pairs:
            result.skipped.append(k)
        else:
            pairs[k] = v
            result.added.append(k)

    for k, v in (update or {}).items():
        if k not in pairs and not overwrite:
            result.skipped.append(k)
        elif k not in pairs:
            pairs[k] = v
            result.added.append(k)
        else:
            pairs[k] = v
            result.updated.append(k)

    for k in (remove or []):
        if k in pairs:
            del pairs[k]
            result.removed.append(k)
        else:
            result.skipped.append(k)

    target.write_text(_render_env(pairs))
    return result
