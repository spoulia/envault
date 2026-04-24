"""Cross-check two .env files to verify all keys in a reference file exist
and have non-empty values in a target file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CrossCheckIssue:
    key: str
    kind: str  # 'missing' | 'empty'
    message: str


@dataclass
class CrossCheckResult:
    issues: List[CrossCheckIssue] = field(default_factory=list)
    checked: int = 0
    reference_file: str = ""
    target_file: str = ""


def has_issues(result: CrossCheckResult) -> bool:
    return len(result.issues) > 0


def _parse_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def cross_check(
    reference: Path,
    target: Path,
    allow_empty: bool = False,
    keys: Optional[List[str]] = None,
) -> CrossCheckResult:
    """Check that all keys in *reference* are present (and optionally non-empty)
    in *target*."""
    if not reference.exists():
        raise FileNotFoundError(f"Reference file not found: {reference}")
    if not target.exists():
        raise FileNotFoundError(f"Target file not found: {target}")

    ref_env = _parse_env(reference)
    tgt_env = _parse_env(target)

    candidates = keys if keys else list(ref_env.keys())
    issues: List[CrossCheckIssue] = []

    for key in candidates:
        if key not in tgt_env:
            issues.append(
                CrossCheckIssue(key=key, kind="missing",
                                message=f"Key '{key}' is missing from target")
            )
        elif not allow_empty and tgt_env[key] == "":
            issues.append(
                CrossCheckIssue(key=key, kind="empty",
                                message=f"Key '{key}' is empty in target")
            )

    return CrossCheckResult(
        issues=issues,
        checked=len(candidates),
        reference_file=str(reference),
        target_file=str(target),
    )


def format_cross_check(result: CrossCheckResult) -> str:
    lines = [
        f"Cross-check: {result.reference_file} → {result.target_file}",
        f"Checked {result.checked} key(s).",
    ]
    if not result.issues:
        lines.append("All keys present and non-empty. ✓")
    else:
        for issue in result.issues:
            tag = "[MISSING]" if issue.kind == "missing" else "[EMPTY]"
            lines.append(f"  {tag} {issue.message}")
    return "\n".join(lines)
