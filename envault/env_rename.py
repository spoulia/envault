"""Rename keys inside a decrypted .env file or vault."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RenameResult:
    renamed: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    not_found: list[str] = field(default_factory=list)


def _parse_env(text: str) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            lines.append(("", line))
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            lines.append((k.strip(), v))
        else:
            lines.append(("", line))
    return lines


def _render_env(lines: list[tuple[str, str]]) -> str:
    parts = []
    for k, v in lines:
        if k == "":
            parts.append(v)
        else:
            parts.append(f"{k}={v}")
    return "\n".join(parts)


def rename_keys(
    src: Path,
    mapping: dict[str, str],
    dst: Optional[Path] = None,
    overwrite: bool = False,
) -> RenameResult:
    """Rename keys in *src* according to *mapping* {old: new}.
    Writes result to *dst* (defaults to *src*).
    """
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    text = src.read_text()
    lines = _parse_env(text)
    existing_keys = {k for k, _ in lines if k}
    result = RenameResult()

    for old, new in mapping.items():
        if old not in existing_keys:
            result.not_found.append(old)
        elif new in existing_keys and not overwrite:
            result.skipped.append(old)
        else:
            result.renamed.append((old, new))

    renamed_map = dict(result.renamed)
    new_lines = []
    for k, v in lines:
        if k in renamed_map:
            new_lines.append((renamed_map[k], v))
        else:
            new_lines.append((k, v))

    out = dst or src
    out.write_text(_render_env(new_lines))
    return result
