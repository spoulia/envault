"""Sort keys in a .env file alphabetically or by custom order."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class SortResult:
    path: str
    original_order: List[str]
    sorted_order: List[str]
    changed: bool


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return list of (key, raw_line) preserving comments/blanks as ('', line)."""
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            pairs.append(("", line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            pairs.append((key, line))
        else:
            pairs.append(("", line))
    return pairs


def _render_env(pairs: list[tuple[str, str]]) -> str:
    return "\n".join(line for _, line in pairs) + "\n"


def sort_file(
    path: Path,
    *,
    reverse: bool = False,
    group_comments: bool = True,
    dry_run: bool = False,
) -> SortResult:
    """Sort key=value lines alphabetically, preserving comment blocks above keys."""
    text = path.read_text()
    pairs = _parse_env(text)

    # Separate into blocks: each block = leading comment lines + one key line
    blocks: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    for key, line in pairs:
        if key == "":
            current.append((key, line))
        else:
            current.append((key, line))
            blocks.append(current)
            current = []
    # trailing blanks/comments
    if current:
        blocks.append(current)

    def block_key(block: list[tuple[str, str]]) -> str:
        for k, _ in block:
            if k:
                return k.lower()
        return "\xff"  # sort trailing blanks to end

    original_order = [block_key(b) for b in blocks]
    sorted_blocks = sorted(blocks, key=block_key, reverse=reverse)
    sorted_order = [block_key(b) for b in sorted_blocks]
    changed = original_order != sorted_order

    if changed and not dry_run:
        flat = [(k, l) for block in sorted_blocks for k, l in block]
        path.write_text(_render_env(flat))

    return SortResult(
        path=str(path),
        original_order=[o for o in original_order if o != "\xff"],
        sorted_order=[o for o in sorted_order if o != "\xff"],
        changed=changed,
    )
