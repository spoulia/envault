"""Generate .env files from a set of key definitions with optional defaults and types."""
from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class KeySpec:
    name: str
    default: Optional[str] = None
    required: bool = False
    secret: bool = False  # auto-generate a random value
    secret_length: int = 32
    comment: Optional[str] = None


@dataclass
class GenerateResult:
    generated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    output_path: Optional[str] = None


_ALPHABET = string.ascii_letters + string.digits


def _random_secret(length: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def _render_env(pairs: Dict[str, str], specs: List[KeySpec]) -> str:
    lines: List[str] = []
    spec_map = {s.name: s for s in specs}
    for key, value in pairs.items():
        spec = spec_map.get(key)
        if spec and spec.comment:
            lines.append(f"# {spec.comment}")
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def generate(specs: List[KeySpec], output: str, overwrite: bool = False) -> GenerateResult:
    """Generate an .env file from key specs."""
    out_path = Path(output)
    existing: Dict[str, str] = {}

    if out_path.exists():
        for line in out_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                existing[k.strip()] = v.strip()

    result = GenerateResult(output_path=output)
    pairs: Dict[str, str] = dict(existing)

    for spec in specs:
        if spec.name in existing and not overwrite:
            result.skipped.append(spec.name)
            continue
        if spec.secret:
            pairs[spec.name] = _random_secret(spec.secret_length)
        elif spec.default is not None:
            pairs[spec.name] = spec.default
        elif spec.required:
            pairs[spec.name] = ""
        else:
            pairs[spec.name] = ""
        result.generated.append(spec.name)

    out_path.write_text(_render_env(pairs, specs))
    return result
