"""Auto-fix common .env lint issues in place."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class FixResult:
    path: Path
    original_lines: List[str]
    fixed_lines: List[str]
    fixes: List[Tuple[int, str]]  # (line_number, description)

    @property
    def fix_count(self) -> int:
        return len(self.fixes)

    @property
    def changed(self) -> bool:
        return self.original_lines != self.fixed_lines


def _fix_line(line: str, lineno: int) -> Tuple[str, List[Tuple[int, str]]]:
    """Apply all auto-fixable rules to a single line."""
    fixes: List[Tuple[int, str]] = []
    original = line

    # Skip blank lines and comment lines
    stripped = line.rstrip("\n")
    if not stripped or stripped.lstrip().startswith("#"):
        return line, fixes

    # Must contain '=' to be a key=value pair
    if "=" not in stripped:
        return line, fixes

    key, _, value = stripped.partition("=")

    # Fix: strip whitespace around key
    clean_key = key.strip()
    if clean_key != key:
        fixes.append((lineno, f"stripped whitespace from key '{clean_key}'"))
        key = clean_key

    # Fix: strip whitespace around value (but not inside quotes)
    clean_value = value.strip()
    if clean_value != value:
        fixes.append((lineno, f"stripped whitespace from value of '{key}'"))
        value = clean_value

    # Fix: uppercase key
    upper_key = key.upper()
    if upper_key != key:
        fixes.append((lineno, f"uppercased key '{key}' -> '{upper_key}'"))
        key = upper_key

    # Fix: remove unnecessary surrounding double-quotes from simple values
    if (
        len(value) >= 2
        and value.startswith('"')
        and value.endswith('"')
        and " " not in value[1:-1]
        and "$" not in value[1:-1]
        and "'" not in value[1:-1]
    ):
        unquoted = value[1:-1]
        fixes.append((lineno, f"removed unnecessary quotes from value of '{key}'"))
        value = unquoted

    new_line = f"{key}={value}\n"
    if not original.endswith("\n"):
        new_line = new_line.rstrip("\n")
    return new_line, fixes


def lint_fix(path: Path) -> FixResult:
    """Read *path*, apply all auto-fixable rules, and write the result back."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    original_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    fixed_lines: List[str] = []
    all_fixes: List[Tuple[int, str]] = []

    for i, line in enumerate(original_lines, start=1):
        new_line, fixes = _fix_line(line, i)
        fixed_lines.append(new_line)
        all_fixes.extend(fixes)

    result = FixResult(
        path=path,
        original_lines=original_lines,
        fixed_lines=fixed_lines,
        fixes=all_fixes,
    )

    if result.changed:
        path.write_text("".join(fixed_lines), encoding="utf-8")

    return result
