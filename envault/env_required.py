"""Check that required keys are present and non-empty in an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class RequiredIssue:
    key: str
    reason: str  # 'missing' | 'empty'


@dataclass
class RequiredResult:
    path: str
    issues: List[RequiredIssue] = field(default_factory=list)
    checked: List[str] = field(default_factory=list)


def has_issues(result: RequiredResult) -> bool:
    return len(result.issues) > 0


def _parse_env(text: str) -> dict:
    env = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def check_required(
    path: Path,
    required_keys: List[str],
    allow_empty: bool = False,
) -> RequiredResult:
    """Verify that *required_keys* exist (and optionally are non-empty) in *path*."""
    result = RequiredResult(path=str(path), checked=list(required_keys))

    if not path.exists():
        for key in required_keys:
            result.issues.append(RequiredIssue(key=key, reason="missing"))
        return result

    env = _parse_env(path.read_text())

    for key in required_keys:
        if key not in env:
            result.issues.append(RequiredIssue(key=key, reason="missing"))
        elif not allow_empty and env[key] == "":
            result.issues.append(RequiredIssue(key=key, reason="empty"))

    return result
