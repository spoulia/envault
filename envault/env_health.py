"""Health check for .env files: detects common issues in one pass."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class HealthIssue:
    key: str
    level: str  # 'error' | 'warning' | 'info'
    message: str


@dataclass
class HealthResult:
    issues: List[HealthIssue] = field(default_factory=list)
    total_keys: int = 0

    @property
    def errors(self) -> List[HealthIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[HealthIssue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def healthy(self) -> bool:
        return len(self.errors) == 0


def _parse_env(path: Path) -> list[tuple[int, str]]:
    lines = []
    for i, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append((i, line))
    return lines


def check_health(env_path: Path) -> HealthResult:
    result = HealthResult()
    if not env_path.exists():
        result.issues.append(HealthIssue("", "error", f"File not found: {env_path}"))
        return result

    seen_keys: dict[str, int] = {}
    lines = _parse_env(env_path)
    result.total_keys = len(lines)

    for lineno, line in lines:
        if "=" not in line:
            result.issues.append(HealthIssue("", "error", f"Line {lineno}: missing '=' separator"))
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            result.issues.append(HealthIssue(key, "error", f"Line {lineno}: empty key"))
        elif key != key.upper():
            result.issues.append(HealthIssue(key, "warning", f"Key '{key}' is not uppercase"))

        if key in seen_keys:
            result.issues.append(HealthIssue(key, "warning", f"Duplicate key '{key}' (first at line {seen_keys[key]})"))
        else:
            seen_keys[key] = lineno

        if value in ("", "CHANGE_ME", "TODO", "<your_value>"):
            result.issues.append(HealthIssue(key, "info", f"Key '{key}' has a placeholder or empty value"))

    return result
