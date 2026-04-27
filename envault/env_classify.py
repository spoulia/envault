"""Classify .env keys into categories based on naming conventions and value patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "secret": [r"SECRET", r"PASSWORD", r"PASSWD", r"TOKEN", r"API_KEY", r"PRIVATE", r"CREDENTIAL"],
    "database": [r"DB_", r"DATABASE", r"POSTGRES", r"MYSQL", r"MONGO", r"REDIS"],
    "network": [r"HOST", r"PORT", r"URL", r"URI", r"ENDPOINT", r"DOMAIN", r"ADDR"],
    "feature_flag": [r"ENABLE_", r"DISABLE_", r"FEATURE_", r"FLAG_"],
    "path": [r"PATH", r"DIR", r"DIRECTORY", r"FILE", r"FOLDER"],
    "debug": [r"DEBUG", r"LOG", r"VERBOSE", r"TRACE"],
}


@dataclass
class ClassifyResult:
    categories: Dict[str, List[str]] = field(default_factory=dict)
    unclassified: List[str] = field(default_factory=list)
    total_keys: int = 0

    @property
    def classified_count(self) -> int:
        return sum(len(v) for v in self.categories.values())

    @property
    def unclassified_count(self) -> int:
        return len(self.unclassified)


def _parse_env(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _classify_key(key: str) -> str | None:
    upper = key.upper()
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(re.search(p, upper) for p in patterns):
            return category
    return None


def classify_file(env_path: Path) -> ClassifyResult:
    if not env_path.exists():
        raise FileNotFoundError(f"File not found: {env_path}")

    env = _parse_env(env_path)
    categories: Dict[str, List[str]] = {}
    unclassified: List[str] = []

    for key in env:
        cat = _classify_key(key)
        if cat:
            categories.setdefault(cat, []).append(key)
        else:
            unclassified.append(key)

    return ClassifyResult(
        categories=categories,
        unclassified=unclassified,
        total_keys=len(env),
    )


def format_classify(result: ClassifyResult) -> str:
    lines: List[str] = []
    for cat, keys in sorted(result.categories.items()):
        lines.append(f"[{cat}]")
        for k in sorted(keys):
            lines.append(f"  {k}")
    if result.unclassified:
        lines.append("[unclassified]")
        for k in sorted(result.unclassified):
            lines.append(f"  {k}")
    return "\n".join(lines)
