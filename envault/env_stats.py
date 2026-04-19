"""Compute statistics about a .env file."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class StatsResult:
    total_keys: int = 0
    empty_values: int = 0
    placeholder_values: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    duplicate_keys: List[str] = field(default_factory=list)
    prefix_counts: Dict[str, int] = field(default_factory=dict)


_PLACEHOLDER_RE = re.compile(r'^<.+>$|^\{\{.+\}\}$|^CHANGEME$|^TODO$', re.IGNORECASE)


def _parse_lines(lines: List[str]):
    keys = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            yield ('blank', None, None)
        elif stripped.startswith('#'):
            yield ('comment', None, None)
        elif '=' in stripped:
            key, _, value = stripped.partition('=')
            yield ('entry', key.strip(), value.strip())
        else:
            yield ('entry', stripped, '')


def compute_stats(path: Path) -> StatsResult:
    """Return a StatsResult for the given .env file."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    lines = path.read_text().splitlines()
    result = StatsResult()
    seen: Dict[str, int] = {}

    for kind, key, value in _parse_lines(lines):
        if kind == 'blank':
            result.blank_lines += 1
        elif kind == 'comment':
            result.comment_lines += 1
        elif kind == 'entry':
            result.total_keys += 1
            seen[key] = seen.get(key, 0) + 1
            if value == '':
                result.empty_values += 1
            elif _PLACEHOLDER_RE.match(value):
                result.placeholder_values += 1
            if '_' in key:
                prefix = key.split('_')[0]
                result.prefix_counts[prefix] = result.prefix_counts.get(prefix, 0) + 1

    result.duplicate_keys = [k for k, count in seen.items() if count > 1]
    return result
