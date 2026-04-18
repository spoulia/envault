"""Search across vault keys and values."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from envault.vault import unlock


@dataclass
class SearchResult:
    vault: str
    key: str
    value: str
    line: int


def _parse_env(text: str) -> list[tuple[int, str, str]]:
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        results.append((i, k.strip(), v.strip()))
    return results


def search_vault(
    vault_path: str | Path,
    password: str,
    pattern: str,
    search_values: bool = False,
    ignore_case: bool = False,
) -> list[SearchResult]:
    """Search keys (and optionally values) in a vault for pattern."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")
    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags)
    plaintext = unlock(str(vault_path), password)
    entries = _parse_env(plaintext)
    results = []
    for lineno, key, value in entries:
        key_match = regex.search(key)
        val_match = regex.search(value) if search_values else None
        if key_match or val_match:
            results.append(SearchResult(vault=str(vault_path), key=key, value=value, line=lineno))
    return results


def search_many(
    vault_paths: list[str | Path],
    password: str,
    pattern: str,
    search_values: bool = False,
    ignore_case: bool = False,
) -> list[SearchResult]:
    """Search across multiple vaults."""
    all_results: list[SearchResult] = []
    for vp in vault_paths:
        try:
            all_results.extend(search_vault(vp, password, pattern, search_values, ignore_case))
        except (FileNotFoundError, ValueError):
            continue
    return all_results
