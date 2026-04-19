"""Search env files for keys/values matching a regex pattern."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class GrepMatch:
    file: str
    key: str
    value: str
    line_number: int


@dataclass
class GrepResult:
    matches: List[GrepMatch] = field(default_factory=list)
    pattern: str = ""
    files_searched: int = 0

    @property
    def match_count(self) -> int:
        return len(self.matches)


def _parse_env(text: str):
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        yield i, key.strip(), value.strip()


def grep_files(
    paths: List[Path],
    pattern: str,
    search_values: bool = True,
    search_keys: bool = True,
    ignore_case: bool = False,
) -> GrepResult:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {exc}") from exc

    result = GrepResult(pattern=pattern)
    for path in paths:
        if not path.exists():
            continue
        result.files_searched += 1
        text = path.read_text(encoding="utf-8")
        for lineno, key, value in _parse_env(text):
            key_hit = search_keys and bool(rx.search(key))
            val_hit = search_values and bool(rx.search(value))
            if key_hit or val_hit:
                result.matches.append(
                    GrepMatch(file=str(path), key=key, value=value, line_number=lineno)
                )
    return result


def format_grep(result: GrepResult, show_values: bool = False) -> str:
    if not result.matches:
        return "No matches found."
    lines = []
    for m in result.matches:
        val_part = f"={m.value}" if show_values else ""
        lines.append(f"{m.file}:{m.line_number}: {m.key}{val_part}")
    return "\n".join(lines)
