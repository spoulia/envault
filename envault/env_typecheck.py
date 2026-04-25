"""Type-checking for .env values against a simple type registry."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_TYPES = {"str", "int", "float", "bool", "url", "email", "json"}

_URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class TypeIssue:
    key: str
    expected: str
    actual_value: str
    message: str


@dataclass
class TypeCheckResult:
    issues: List[TypeIssue] = field(default_factory=list)
    checked: int = 0
    skipped: int = 0


def has_issues(result: TypeCheckResult) -> bool:
    return len(result.issues) > 0


def _parse_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _check_type(value: str, expected: str) -> Optional[str]:
    if expected == "int":
        try:
            int(value)
        except ValueError:
            return f"expected int, got {value!r}"
    elif expected == "float":
        try:
            float(value)
        except ValueError:
            return f"expected float, got {value!r}"
    elif expected == "bool":
        if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
            return f"expected bool, got {value!r}"
    elif expected == "url":
        if not _URL_RE.match(value):
            return f"expected url, got {value!r}"
    elif expected == "email":
        if not _EMAIL_RE.match(value):
            return f"expected email, got {value!r}"
    elif expected == "json":
        try:
            json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return f"expected valid JSON, got {value!r}"
    return None


def typecheck_env(
    env_path: Path,
    type_map: Dict[str, str],
) -> TypeCheckResult:
    """Check values in env_path against type_map {KEY: type_name}."""
    env = _parse_env(env_path)
    result = TypeCheckResult()
    for key, expected in type_map.items():
        if expected not in VALID_TYPES:
            result.skipped += 1
            continue
        if key not in env:
            result.skipped += 1
            continue
        result.checked += 1
        msg = _check_type(env[key], expected)
        if msg:
            result.issues.append(TypeIssue(key=key, expected=expected, actual_value=env[key], message=msg))
    return result
