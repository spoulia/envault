"""env_diff_merge.py – three-way merge for .env files.

Given a *base* version and two *derived* versions (ours / theirs), produce
a merged result that:
  - keeps keys only in ours
  - keeps keys only in theirs
  - keeps keys unchanged from base in both sides
  - auto-resolves when only one side changed a key
  - flags a *conflict* when both sides changed the same key differently
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeConflict:
    """A key whose value diverged on both sides."""

    key: str
    base_value: Optional[str]
    ours_value: str
    theirs_value: str


@dataclass
class DiffMergeResult:
    """Outcome of a three-way merge operation."""

    merged: Dict[str, str]          # final key→value map (conflicts use *ours*)
    conflicts: List[MergeConflict] = field(default_factory=list)
    auto_resolved: int = 0          # keys resolved without conflict

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_env(text: str) -> Dict[str, str]:
    """Parse a .env file text into an ordered key→value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def _render_env(mapping: Dict[str, str]) -> str:
    """Render a key→value dict back to .env format."""
    return "\n".join(f"{k}={v}" for k, v in mapping.items()) + "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def diff_merge(
    base: Dict[str, str],
    ours: Dict[str, str],
    theirs: Dict[str, str],
) -> DiffMergeResult:
    """Three-way merge of three key→value dicts.

    Resolution rules (in priority order):
    1. Both sides agree on a value → use it.
    2. Only *ours* changed relative to base → use ours.
    3. Only *theirs* changed relative to base → use theirs.
    4. Both sides changed to the *same* new value → use it (no conflict).
    5. Both sides changed to *different* values → conflict; keep ours.
    """
    all_keys = set(base) | set(ours) | set(theirs)
    merged: Dict[str, str] = {}
    conflicts: List[MergeConflict] = []
    auto_resolved = 0

    for key in sorted(all_keys):
        base_val = base.get(key)
        our_val = ours.get(key)
        their_val = theirs.get(key)

        our_changed = our_val != base_val
        their_changed = their_val != base_val

        if not our_changed and not their_changed:
            # Unchanged on both sides – keep base (or absent if deleted everywhere)
            if base_val is not None:
                merged[key] = base_val
            auto_resolved += 1

        elif our_changed and not their_changed:
            # Only we changed it
            if our_val is not None:
                merged[key] = our_val
            auto_resolved += 1

        elif their_changed and not our_changed:
            # Only they changed it
            if their_val is not None:
                merged[key] = their_val
            auto_resolved += 1

        else:
            # Both sides changed – check if they agree
            if our_val == their_val:
                if our_val is not None:
                    merged[key] = our_val
                auto_resolved += 1
            else:
                # Real conflict – keep ours, record conflict
                if our_val is not None:
                    merged[key] = our_val
                conflicts.append(
                    MergeConflict(
                        key=key,
                        base_value=base_val,
                        ours_value=our_val or "",
                        theirs_value=their_val or "",
                    )
                )

    return DiffMergeResult(merged=merged, conflicts=conflicts, auto_resolved=auto_resolved)


def merge_files(
    base_path: Path,
    ours_path: Path,
    theirs_path: Path,
    output_path: Optional[Path] = None,
) -> Tuple[DiffMergeResult, str]:
    """Load three .env files, merge them, optionally write result.

    Returns (result, rendered_text).
    """
    base = _parse_env(base_path.read_text(encoding="utf-8"))
    ours = _parse_env(ours_path.read_text(encoding="utf-8"))
    theirs = _parse_env(theirs_path.read_text(encoding="utf-8"))

    result = diff_merge(base, ours, theirs)
    rendered = _render_env(result.merged)

    if output_path is not None:
        output_path.write_text(rendered, encoding="utf-8")

    return result, rendered
