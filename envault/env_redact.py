"""Redact sensitive values from .env files for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

DEFAULT_SENSITIVE_PATTERNS = (
    "SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY",
    "PRIVATE", "CREDENTIALS", "AUTH", "KEY",
)

REDACT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: dict[str, str]
    redacted: dict[str, str]
    redacted_keys: list[str] = field(default_factory=list)


def _parse_env(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def _render_env(pairs: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def _is_sensitive(key: str, patterns: Iterable[str]) -> bool:
    upper = key.upper()
    return any(p in upper for p in patterns)


def redact(
    source: Path,
    patterns: Iterable[str] = DEFAULT_SENSITIVE_PATTERNS,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    if not source.exists():
        raise FileNotFoundError(f"{source} not found")
    text = source.read_text()
    original = _parse_env(text)
    redacted: dict[str, str] = {}
    redacted_keys: list[str] = []
    for key, value in original.items():
        if _is_sensitive(key, patterns):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value
    return RedactResult(original=original, redacted=redacted, redacted_keys=redacted_keys)


def redact_to_file(
    source: Path,
    dest: Path,
    patterns: Iterable[str] = DEFAULT_SENSITIVE_PATTERNS,
    placeholder: str = REDACT_PLACEHOLDER,
) -> RedactResult:
    result = redact(source, patterns=patterns, placeholder=placeholder)
    dest.write_text(_render_env(result.redacted))
    return result
