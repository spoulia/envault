"""env_supersede: replace keys in a target .env file with values from a source."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SupersedeResult:
    source: str
    target: str
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def added_count(self) -> int:
        return len(self.added)


def _parse_env(path: Path) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def _render_env(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def supersede(
    source: Path,
    target: Path,
    keys: Optional[List[str]] = None,
    add_missing: bool = True,
    overwrite: bool = True,
    dry_run: bool = False,
) -> SupersedeResult:
    """Supersede keys in *target* with values from *source*."""
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    if not target.exists():
        raise FileNotFoundError(f"Target file not found: {target}")

    src = _parse_env(source)
    dst = _parse_env(target)

    result = SupersedeResult(source=str(source), target=str(target))
    candidates = keys if keys is not None else list(src.keys())

    for key in candidates:
        if key not in src:
            result.skipped.append(key)
            continue
        if key in dst:
            if overwrite:
                dst[key] = src[key]
                result.applied.append(key)
            else:
                result.skipped.append(key)
        else:
            if add_missing:
                dst[key] = src[key]
                result.added.append(key)
            else:
                result.skipped.append(key)

    if not dry_run:
        target.write_text(_render_env(dst))

    return result
