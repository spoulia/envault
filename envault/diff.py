"""Diff two .env vault files to show added/removed/changed keys."""
from __future__ import annotations
from typing import NamedTuple
from envault.vault import unlock


class DiffResult(NamedTuple):
    added: dict[str, str]
    removed: dict[str, str]
    changed: dict[str, tuple[str, str]]  # key -> (old, new)


def _parse_env(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def diff_vaults(
    vault_a: str,
    password_a: str,
    vault_b: str,
    password_b: str,
) -> DiffResult:
    """Decrypt two vault files and return a structured diff."""
    text_a = unlock(vault_a, password_a)
    text_b = unlock(vault_b, password_b)
    env_a = _parse_env(text_a)
    env_b = _parse_env(text_b)

    keys_a = set(env_a)
    keys_b = set(env_b)

    added = {k: env_b[k] for k in keys_b - keys_a}
    removed = {k: env_a[k] for k in keys_a - keys_b}
    changed = {
        k: (env_a[k], env_b[k])
        for k in keys_a & keys_b
        if env_a[k] != env_b[k]
    }
    return DiffResult(added=added, removed=removed, changed=changed)


def format_diff(result: DiffResult) -> str:
    lines: list[str] = []
    for key, value in sorted(result.added.items()):
        lines.append(f"+ {key}={value}")
    for key, value in sorted(result.removed.items()):
        lines.append(f"- {key}={value}")
    for key, (old, new) in sorted(result.changed.items()):
        lines.append(f"~ {key}: {old!r} -> {new!r}")
    return "\n".join(lines) if lines else "(no differences)"
