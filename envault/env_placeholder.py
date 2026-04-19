"""Detect and resolve placeholder values in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import re

_PLACEHOLDER_PATTERNS = [
    re.compile(r'^CHANGE_ME$', re.IGNORECASE),
    re.compile(r'^TODO$', re.IGNORECASE),
    re.compile(r'^PLACEHOLDER$', re.IGNORECASE),
    re.compile(r'^<.*>$'),
    re.compile(r'^\$\{.*\}$'),
    re.compile(r'^your[_\-]', re.IGNORECASE),
    re.compile(r'^xxx+$', re.IGNORECASE),
]


@dataclass
class PlaceholderIssue:
    key: str
    value: str
    reason: str


@dataclass
class PlaceholderResult:
    issues: List[PlaceholderIssue] = field(default_factory=list)
    resolved: Dict[str, str] = field(default_factory=dict)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, _, v = line.partition('=')
            result[k.strip()] = v.strip()
    return result


def _is_placeholder(value: str) -> bool:
    return any(p.match(value) for p in _PLACEHOLDER_PATTERNS)


def scan_placeholders(env_path: Path) -> PlaceholderResult:
    """Scan an env file for placeholder values."""
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} not found")
    text = env_path.read_text()
    pairs = _parse_env(text)
    result = PlaceholderResult()
    for key, value in pairs.items():
        if _is_placeholder(value):
            result.issues.append(PlaceholderIssue(key=key, value=value, reason="placeholder value detected"))
    return result


def resolve_placeholders(env_path: Path, replacements: Dict[str, str], overwrite: bool = False) -> PlaceholderResult:
    """Replace placeholder values with real ones."""
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} not found")
    text = env_path.read_text()
    pairs = _parse_env(text)
    result = PlaceholderResult()
    lines = text.splitlines(keepends=True)
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            new_lines.append(line)
            continue
        k, _, v = stripped.partition('=')
        k = k.strip()
        if k in replacements and (_is_placeholder(v.strip()) or overwrite):
            new_lines.append(f"{k}={replacements[k]}\n")
            result.resolved[k] = replacements[k]
        else:
            new_lines.append(line)
    env_path.write_text(''.join(new_lines))
    return result
