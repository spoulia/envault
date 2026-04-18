"""Validate .env files against a schema (required keys, patterns, types)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str  # "error" | "warning"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def _parse_env(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def validate_file(
    env_path: Path,
    required: Optional[list[str]] = None,
    patterns: Optional[dict[str, str]] = None,
    nonempty: Optional[list[str]] = None,
) -> ValidationResult:
    """Validate an env file against simple rules."""
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} not found")

    result = ValidationResult()
    env = _parse_env(env_path.read_text())

    for key in required or []:
        if key not in env:
            result.issues.append(ValidationIssue(key, "required key is missing", "error"))

    for key in nonempty or []:
        if key in env and env[key] == "":
            result.issues.append(ValidationIssue(key, "value must not be empty", "error"))

    for key, pattern in (patterns or {}).items():
        if key in env and not re.fullmatch(pattern, env[key]):
            result.issues.append(
                ValidationIssue(key, f"value does not match pattern '{pattern}'", "warning")
            )

    return result
