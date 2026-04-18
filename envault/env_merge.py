"""Merge multiple .env files or vaults into one, with conflict resolution."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Tuple

Strategy = Literal["first", "last", "error"]


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[Tuple[str, List[str]]]  # (key, [values...])
    sources: List[str]


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _render_env(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items())) + "\n"


def merge_files(
    paths: List[Path],
    strategy: Strategy = "last",
) -> MergeResult:
    """Merge multiple .env files according to the given conflict strategy."""
    all_keys: Dict[str, List[str]] = {}
    source_names = [str(p) for p in paths]

    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        data = _parse_env(path.read_text())
        for k, v in data.items():
            all_keys.setdefault(k, []).append(v)

    merged: Dict[str, str] = {}
    conflicts: List[Tuple[str, List[str]]] = []

    for key, values in all_keys.items():
        unique = list(dict.fromkeys(values))
        if len(unique) > 1:
            conflicts.append((key, unique))
            if strategy == "error":
                raise ValueError(f"Conflict on key '{key}': {unique}")
            elif strategy == "first":
                merged[key] = values[0]
            else:  # last
                merged[key] = values[-1]
        else:
            merged[key] = unique[0]

    return MergeResult(merged=merged, conflicts=conflicts, sources=source_names)


def write_merged(result: MergeResult, dest: Path) -> None:
    dest.write_text(_render_env(result.merged))
