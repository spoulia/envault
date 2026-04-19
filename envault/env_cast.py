"""Type-casting utilities for .env values."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_TYPES = ("str", "int", "float", "bool")


@dataclass
class CastResult:
    casted: dict[str, Any] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _parse_env(path: Path) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        pairs[k.strip()] = v.strip()
    return pairs


def _cast_value(value: str, type_name: str) -> Any:
    if type_name == "int":
        return int(value)
    if type_name == "float":
        return float(value)
    if type_name == "bool":
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ValueError(f"Cannot cast {value!r} to bool")
    return value  # str


def cast_env(path: Path, rules: dict[str, str]) -> CastResult:
    """Cast env values according to rules mapping key -> type name."""
    pairs = _parse_env(path)
    result = CastResult()
    for key, raw in pairs.items():
        type_name = rules.get(key)
        if type_name is None:
            result.skipped.append(key)
            result.casted[key] = raw
            continue
        if type_name not in SUPPORTED_TYPES:
            result.errors.append(f"{key}: unsupported type '{type_name}'")
            result.casted[key] = raw
            continue
        try:
            result.casted[key] = _cast_value(raw, type_name)
        except (ValueError, TypeError) as exc:
            result.errors.append(f"{key}: {exc}")
            result.casted[key] = raw
    return result
