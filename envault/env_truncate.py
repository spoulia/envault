"""env_truncate: truncate long env variable values to a maximum length."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TruncateResult:
    path: Path
    entries: Dict[str, str]          # final key -> value mapping
    truncated: List[str]             # keys whose values were shortened
    skipped: List[str]               # keys already within the limit


def truncated_count(result: TruncateResult) -> int:
    return len(result.truncated)


def skipped_count(result: TruncateResult) -> int:
    return len(result.skipped)


def _parse_env(text: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def _render_env(pairs: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs.items()) + "\n"


def truncate_file(
    path: Path,
    max_length: int = 64,
    suffix: str = "...",
    keys: Optional[List[str]] = None,
    write: bool = True,
) -> TruncateResult:
    """Truncate values longer than *max_length* characters.

    Args:
        path:       Path to the .env file.
        max_length: Maximum allowed value length (including suffix).
        suffix:     String appended to truncated values.
        keys:       If given, only these keys are considered.
        write:      Persist the result back to *path* when True.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    pairs = _parse_env(text)

    truncated: List[str] = []
    skipped: List[str] = []
    result_pairs: Dict[str, str] = {}

    effective_max = max(len(suffix), max_length)

    for key, value in pairs.items():
        if keys is not None and key not in keys:
            result_pairs[key] = value
            continue
        if len(value) > max_length:
            cut = effective_max - len(suffix)
            result_pairs[key] = value[:cut] + suffix
            truncated.append(key)
        else:
            result_pairs[key] = value
            skipped.append(key)

    if write:
        path.write_text(_render_env(result_pairs), encoding="utf-8")

    return TruncateResult(
        path=path,
        entries=result_pairs,
        truncated=truncated,
        skipped=skipped,
    )
