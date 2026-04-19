"""Mask sensitive values in .env files for safe display."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SENSITIVE_PATTERNS = (
    "SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY",
    "PRIVATE", "AUTH", "CREDENTIAL", "CERT", "KEY",
)


@dataclass
class MaskResult:
    masked: dict[str, str]
    masked_keys: list[str] = field(default_factory=list)
    total: int = 0


def _parse_env(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def _is_sensitive(key: str, extra: Optional[list[str]] = None) -> bool:
    upper = key.upper()
    patterns = list(SENSITIVE_PATTERNS) + [p.upper() for p in (extra or [])]
    return any(p in upper for p in patterns)


def _mask_value(value: str, reveal_chars: int = 0) -> str:
    if not value:
        return value
    if reveal_chars > 0 and len(value) > reveal_chars:
        return value[:reveal_chars] + "*" * (len(value) - reveal_chars)
    return "*" * len(value)


def mask_env(
    path: Path,
    extra_keys: Optional[list[str]] = None,
    reveal_chars: int = 0,
) -> MaskResult:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    text = path.read_text()
    parsed = _parse_env(text)
    masked: dict[str, str] = {}
    masked_keys: list[str] = []
    for k, v in parsed.items():
        if _is_sensitive(k, extra_keys) or (extra_keys and k in extra_keys):
            masked[k] = _mask_value(v, reveal_chars)
            masked_keys.append(k)
        else:
            masked[k] = v
    return MaskResult(masked=masked, masked_keys=masked_keys, total=len(parsed))
