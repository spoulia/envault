"""Lint .env files for common issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line: int
    key: str | None
    message: str
    severity: str  # 'error' | 'warning'


@dataclass
class LintResult:
    path: Path
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def lint_file(path: Path) -> LintResult:
    result = LintResult(path=path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    seen_keys: dict[str, int] = {}
    lines = path.read_text().splitlines()

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            result.issues.append(LintIssue(lineno, None, "Missing '=' separator", "error"))
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            result.issues.append(LintIssue(lineno, key, "Empty key", "error"))
        if key != key.upper():
            result.issues.append(LintIssue(lineno, key, "Key should be uppercase", "warning"))
        if " " in key:
            result.issues.append(LintIssue(lineno, key, "Key contains spaces", "error"))
        if not value:
            result.issues.append(LintIssue(lineno, key, "Empty value", "warning"))
        if key in seen_keys:
            result.issues.append(LintIssue(lineno, key, f"Duplicate key (first at line {seen_keys[key]})", "error"))
        else:
            seen_keys[key] = lineno

    return result
