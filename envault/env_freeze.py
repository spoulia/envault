"""env_freeze.py – snapshot the current values of an env file as a frozen
read-only reference so drift can be detected later."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_FREEZE_FILE = ".envault_freeze.json"


@dataclass
class FreezeResult:
    source: str
    freeze_file: str
    keys_frozen: int
    snapshot: Dict[str, str] = field(default_factory=dict)


@dataclass
class DriftIssue:
    key: str
    kind: str          # 'changed' | 'added' | 'removed'
    frozen_value: Optional[str] = None
    current_value: Optional[str] = None


@dataclass
class DriftResult:
    source: str
    freeze_file: str
    issues: List[DriftIssue] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return len(self.issues) > 0


def _parse_env(path: Path) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        result[k.strip()] = v.strip()
    return result


def freeze(env_path: Path, freeze_path: Optional[Path] = None) -> FreezeResult:
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")
    freeze_path = freeze_path or env_path.parent / _DEFAULT_FREEZE_FILE
    snapshot = _parse_env(env_path)
    data = {"source": str(env_path), "snapshot": snapshot}
    freeze_path.write_text(json.dumps(data, indent=2))
    return FreezeResult(
        source=str(env_path),
        freeze_file=str(freeze_path),
        keys_frozen=len(snapshot),
        snapshot=snapshot,
    )


def check_drift(env_path: Path, freeze_path: Optional[Path] = None) -> DriftResult:
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")
    freeze_path = freeze_path or env_path.parent / _DEFAULT_FREEZE_FILE
    if not freeze_path.exists():
        raise FileNotFoundError(f"Freeze file not found: {freeze_path}")
    data = json.loads(freeze_path.read_text())
    frozen: Dict[str, str] = data.get("snapshot", {})
    current = _parse_env(env_path)
    issues: List[DriftIssue] = []
    for k, fv in frozen.items():
        if k not in current:
            issues.append(DriftIssue(key=k, kind="removed", frozen_value=fv))
        elif current[k] != fv:
            issues.append(DriftIssue(key=k, kind="changed", frozen_value=fv, current_value=current[k]))
    for k, cv in current.items():
        if k not in frozen:
            issues.append(DriftIssue(key=k, kind="added", current_value=cv))
    return DriftResult(source=str(env_path), freeze_file=str(freeze_path), issues=issues)
