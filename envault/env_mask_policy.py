"""env_mask_policy.py – define and enforce masking policies for .env keys."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_POLICY_FILE = Path(".envault") / "mask_policy.json"


@dataclass
class PolicyEntry:
    pattern: str
    action: str  # "mask" | "block" | "allow"
    description: str = ""


@dataclass
class PolicyResult:
    entries: List[PolicyEntry] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.violations)


def _load_policy(policy_file: Path) -> List[PolicyEntry]:
    if not policy_file.exists():
        return []
    data = json.loads(policy_file.read_text())
    return [PolicyEntry(**e) for e in data]


def _save_policy(entries: List[PolicyEntry], policy_file: Path) -> None:
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    policy_file.write_text(
        json.dumps([e.__dict__ for e in entries], indent=2)
    )


def add_policy(
    pattern: str,
    action: str,
    description: str = "",
    policy_file: Path = _DEFAULT_POLICY_FILE,
) -> PolicyEntry:
    if action not in ("mask", "block", "allow"):
        raise ValueError(f"Invalid action '{action}'. Must be mask, block, or allow.")
    entries = _load_policy(policy_file)
    if any(e.pattern == pattern for e in entries):
        raise ValueError(f"Policy for pattern '{pattern}' already exists.")
    entry = PolicyEntry(pattern=pattern, action=action, description=description)
    entries.append(entry)
    _save_policy(entries, policy_file)
    return entry


def remove_policy(pattern: str, policy_file: Path = _DEFAULT_POLICY_FILE) -> bool:
    entries = _load_policy(policy_file)
    new_entries = [e for e in entries if e.pattern != pattern]
    if len(new_entries) == len(entries):
        return False
    _save_policy(new_entries, policy_file)
    return True


def list_policies(policy_file: Path = _DEFAULT_POLICY_FILE) -> List[PolicyEntry]:
    return _load_policy(policy_file)


def enforce_policy(
    env: Dict[str, str],
    policy_file: Path = _DEFAULT_POLICY_FILE,
) -> PolicyResult:
    entries = _load_policy(policy_file)
    violations: List[str] = []
    for key in env:
        for entry in entries:
            if re.search(entry.pattern, key, re.IGNORECASE):
                if entry.action == "block":
                    violations.append(key)
                break
    return PolicyResult(entries=entries, violations=violations)
