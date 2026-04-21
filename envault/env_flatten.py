"""Flatten nested environment variable structures (e.g. JSON values) into dotted keys."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FlattenResult:
    source: Path
    flattened: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)

    @property
    def flattened_count(self) -> int:
        return len(self.flattened)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def _parse_env(path: Path) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def _flatten(prefix: str, obj: Any, out: dict[str, str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten(f"{prefix}.{k}" if prefix else k, v, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _flatten(f"{prefix}.{i}" if prefix else str(i), v, out)
    else:
        out[prefix] = str(obj) if obj is not None else ""


def flatten_env(path: Path) -> FlattenResult:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    pairs = _parse_env(path)
    result = FlattenResult(source=path)

    for key, value in pairs.items():
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (dict, list)):
                _flatten(key, parsed, result.flattened)
            else:
                result.flattened[key] = value
        except (json.JSONDecodeError, ValueError):
            result.flattened[key] = value

    return result


def format_flatten(result: FlattenResult) -> str:
    lines = [f"# Flattened from {result.source}"]
    for k, v in sorted(result.flattened.items()):
        lines.append(f"{k}={v}")
    return "\n".join(lines)
