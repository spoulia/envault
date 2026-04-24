"""Count and summarize keys in one or more .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class CountResult:
    file: str
    total: int
    set_keys: int       # keys with non-empty values
    empty_keys: int     # keys with empty values
    comment_lines: int
    blank_lines: int
    per_prefix: Dict[str, int] = field(default_factory=dict)


def _parse_env(text: str):
    """Yield (key, value) for each real assignment line."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        yield key.strip(), value.strip()


def count_file(path: Path) -> CountResult:
    """Return a CountResult for the given .env file."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
    blank_lines = sum(1 for l in lines if not l.strip())

    pairs = list(_parse_env(text))
    total = len(pairs)
    set_keys = sum(1 for _, v in pairs if v)
    empty_keys = total - set_keys

    per_prefix: Dict[str, int] = {}
    for key, _ in pairs:
        if "_" in key:
            prefix = key.split("_")[0]
            per_prefix[prefix] = per_prefix.get(prefix, 0) + 1

    return CountResult(
        file=str(path),
        total=total,
        set_keys=set_keys,
        empty_keys=empty_keys,
        comment_lines=comment_lines,
        blank_lines=blank_lines,
        per_prefix=per_prefix,
    )


def count_many(paths: List[Path]) -> List[CountResult]:
    """Return CountResult for each path in *paths*."""
    return [count_file(p) for p in paths]


def format_count(result: CountResult) -> str:
    lines = [
        f"File : {result.file}",
        f"Total keys    : {result.total}",
        f"Set keys      : {result.set_keys}",
        f"Empty keys    : {result.empty_keys}",
        f"Comment lines : {result.comment_lines}",
        f"Blank lines   : {result.blank_lines}",
    ]
    if result.per_prefix:
        lines.append("By prefix:")
        for prefix, cnt in sorted(result.per_prefix.items()):
            lines.append(f"  {prefix}_* : {cnt}")
    return "\n".join(lines)
