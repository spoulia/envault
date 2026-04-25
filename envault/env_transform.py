"""Apply transformation rules to .env values (uppercase, lowercase, strip, replace)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    transformed: Dict[str, str]
    changed_keys: List[str]
    skipped_keys: List[str]
    source: str


def changed_count(r: TransformResult) -> int:
    return len(r.changed_keys)


def skipped_count(r: TransformResult) -> int:
    return len(r.skipped_keys)


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


_BUILTIN: Dict[str, Callable[[str], str]] = {
    "uppercase": str.upper,
    "lowercase": str.lower,
    "strip": str.strip,
    "strip_quotes": lambda v: v.strip("'\"" ),
}


def transform_env(
    path: Path,
    operation: str,
    keys: Optional[List[str]] = None,
    *,
    extra: Optional[str] = None,
    write: bool = True,
) -> TransformResult:
    """Apply *operation* to values in *path*.

    Parameters
    ----------
    operation: one of 'uppercase', 'lowercase', 'strip', 'strip_quotes',
               or 'replace:<old>:<new>'.
    keys:      limit to these keys; None means all keys.
    extra:     reserved for future parameterised operations.
    write:     persist changes back to *path* when True.
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    if operation.startswith("replace:"):
        _, old, new = operation.split(":", 2)
        fn: Callable[[str], str] = lambda v, _o=old, _n=new: v.replace(_o, _n)
    elif operation in _BUILTIN:
        fn = _BUILTIN[operation]
    else:
        raise ValueError(f"Unknown operation '{operation}'")

    original = _parse_env(path.read_text())
    result: Dict[str, str] = {}
    changed: List[str] = []
    skipped: List[str] = []

    for k, v in original.items():
        if keys is not None and k not in keys:
            result[k] = v
            skipped.append(k)
            continue
        new_v = fn(v)
        result[k] = new_v
        if new_v != v:
            changed.append(k)
        else:
            skipped.append(k)

    if write:
        path.write_text(_render_env(result))

    return TransformResult(
        transformed=result,
        changed_keys=changed,
        skipped_keys=skipped,
        source=str(path),
    )
