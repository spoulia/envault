"""Compare two vault files side-by-side, showing key presence and value differences."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from envault.vault import unlock


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    same: List[str] = field(default_factory=list)
    different: List[str] = field(default_factory=list)

    @property
    def is_identical(self) -> bool:
        return not (self.only_in_a or self.only_in_b or self.different)


def _parse_env(text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def compare_vaults(
    vault_a: Path,
    password_a: str,
    vault_b: Path,
    password_b: Optional[str] = None,
) -> CompareResult:
    """Decrypt and compare two vault files."""
    if password_b is None:
        password_b = password_a

    env_a = _parse_env(unlock(vault_a, password_a))
    env_b = _parse_env(unlock(vault_b, password_b))

    keys_a = set(env_a)
    keys_b = set(env_b)

    result = CompareResult()
    result.only_in_a = sorted(keys_a - keys_b)
    result.only_in_b = sorted(keys_b - keys_a)

    for key in sorted(keys_a & keys_b):
        if env_a[key] == env_b[key]:
            result.same.append(key)
        else:
            result.different.append(key)

    return result


def format_compare(result: CompareResult, label_a: str = "A", label_b: str = "B") -> str:
    lines: List[str] = []
    for key in result.only_in_a:
        lines.append(f"  only in {label_a}: {key}")
    for key in result.only_in_b:
        lines.append(f"  only in {label_b}: {key}")
    for key in result.different:
        lines.append(f"  changed : {key}")
    for key in result.same:
        lines.append(f"  same    : {key}")
    if result.is_identical:
        lines.append("Vaults are identical.")
    return "\n".join(lines)
