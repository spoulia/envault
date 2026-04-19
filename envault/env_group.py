"""Group .env keys by prefix into named sections."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]

    @property
    def group_names(self) -> List[str]:
        return list(self.groups.keys())


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def group_by_prefix(
    source: Path,
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
) -> GroupResult:
    """Group keys by prefix. If prefixes is None, auto-detect from keys."""
    env = _parse_env(source.read_text())

    if prefixes is None:
        seen: Dict[str, int] = {}
        for key in env:
            if separator in key:
                p = key.split(separator)[0]
                seen[p] = seen.get(p, 0) + 1
        prefixes = [p for p, count in seen.items() if count > 1]

    groups: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix + separator):
                groups[prefix][key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped)


def format_groups(result: GroupResult) -> str:
    lines: List[str] = []
    for group, keys in result.groups.items():
        lines.append(f"[{group}]")
        for k, v in keys.items():
            lines.append(f"  {k}={v}")
        lines.append("")
    if result.ungrouped:
        lines.append("[ungrouped]")
        for k, v in result.ungrouped.items():
            lines.append(f"  {k}={v}")
    return "\n".join(lines)
