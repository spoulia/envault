"""Format .env files: normalize spacing, quoting, and line endings."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class FmtResult:
    path: Path
    changes: List[Tuple[int, str, str]] = field(default_factory=list)  # (lineno, before, after)
    written: bool = False

    @property
    def changed_count(self) -> int:
        return len(self.changes)


def _normalize_line(line: str) -> str:
    """Normalize a single .env line."""
    stripped = line.rstrip("\n")
    # blank or comment lines — preserve as-is
    if not stripped or stripped.lstrip().startswith("#"):
        return stripped

    if "=" not in stripped:
        return stripped

    key, _, value = stripped.partition("=")
    key = key.strip()
    value = value.strip()

    # Remove redundant surrounding quotes when value has none of the special chars
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            inner = value[1:-1]
            if not re.search(r'[\s#$\\]', inner):
                value = inner
            break

    return f"{key}={value}"


def fmt_file(path: Path, *, write: bool = False) -> FmtResult:
    """Format a .env file and optionally write changes back."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    raw_lines = path.read_text().splitlines()
    result = FmtResult(path=path)
    out_lines: List[str] = []

    for i, line in enumerate(raw_lines, start=1):
        normalized = _normalize_line(line)
        if normalized != line:
            result.changes.append((i, line, normalized))
        out_lines.append(normalized)

    if write and result.changes:
        path.write_text("\n".join(out_lines) + "\n")
        result.written = True

    return result
