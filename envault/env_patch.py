"""Apply a patch (set of key-value overrides) to an .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PatchResult:
    source: str
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def removed_count(self) -> int:
        return len(self.removed)


def _parse_env(path: Path) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            pairs[k.strip()] = v.strip()
    return pairs


def _render_env(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def patch_file(
    env_path: Path,
    overrides: Dict[str, str],
    remove_keys: Optional[List[str]] = None,
    overwrite: bool = True,
    output_path: Optional[Path] = None,
) -> PatchResult:
    """Apply *overrides* and optionally remove keys from *env_path*."""
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    result = PatchResult(source=str(env_path))
    pairs = _parse_env(env_path)

    for key, value in overrides.items():
        if key in pairs and not overwrite:
            result.skipped.append(key)
        else:
            pairs[key] = value
            result.applied.append(key)

    for key in remove_keys or []:
        if key in pairs:
            del pairs[key]
            result.removed.append(key)

    dest = output_path or env_path
    dest.write_text(_render_env(pairs))
    return result
