"""Schema validation for .env files against a JSON schema definition."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_TYPES = {"string", "integer", "float", "boolean"}


@dataclass
class SchemaIssue:
    key: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class SchemaResult:
    issues: list[SchemaIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def _parse_env(path: Path) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            pairs[k.strip()] = v.strip()
    return pairs


def _check_type(value: str, expected: str) -> bool:
    try:
        if expected == "integer":
            int(value)
        elif expected == "float":
            float(value)
        elif expected == "boolean":
            if value.lower() not in {"true", "false", "1", "0", "yes", "no"}:
                return False
    except ValueError:
        return False
    return True


def load_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text())


def validate_schema(env_path: Path, schema_path: Path) -> SchemaResult:
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} not found")
    if not schema_path.exists():
        raise FileNotFoundError(f"{schema_path} not found")

    env = _parse_env(env_path)
    schema = load_schema(schema_path)
    result = SchemaResult()

    for key, rules in schema.get("keys", {}).items():
        if rules.get("required", False) and key not in env:
            result.issues.append(SchemaIssue(key, f"Required key '{key}' is missing"))
            continue
        if key not in env:
            continue
        value = env[key]
        expected_type = rules.get("type")
        if expected_type and expected_type in SUPPORTED_TYPES and expected_type != "string":
            if not _check_type(value, expected_type):
                result.issues.append(SchemaIssue(key, f"Expected type '{expected_type}' for key '{key}', got '{value}'"))
        allowed = rules.get("allowed")
        if allowed and value not in allowed:
            result.issues.append(SchemaIssue(key, f"Value '{value}' for '{key}' not in allowed list"))
        pattern = rules.get("pattern")
        if pattern:
            import re
            if not re.fullmatch(pattern, value):
                result.issues.append(SchemaIssue(key, f"Value '{value}' for '{key}' does not match pattern '{pattern}'"))

    return result
