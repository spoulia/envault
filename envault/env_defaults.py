"""Apply default values to missing keys in an .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DefaultsResult:
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return len(self.applied)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def _render_env(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def apply_defaults(
    env_path: Path,
    defaults: Dict[str, str],
    overwrite: bool = False,
    output_path: Optional[Path] = None,
) -> DefaultsResult:
    """Apply *defaults* to the env file, writing missing keys.

    Args:
        env_path: Path to the target .env file.
        defaults: Mapping of key -> default value.
        overwrite: If True, overwrite existing keys with defaults.
        output_path: Write result here; defaults to *env_path*.

    Returns:
        DefaultsResult describing which keys were applied vs skipped.
    """
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    current = _parse_env(env_path.read_text())
    result = DefaultsResult()

    for key, value in defaults.items():
        if key in current and not overwrite:
            result.skipped.append(key)
        else:
            current[key] = value
            result.applied.append(key)

    dest = output_path or env_path
    dest.write_text(_render_env(current))
    return result
