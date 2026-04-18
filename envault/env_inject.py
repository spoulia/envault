"""Inject decrypted .env variables into a subprocess environment."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from envault.vault import unlock


def _parse_env(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def inject_run(
    vault_path: Path,
    password: str,
    command: List[str],
    override: bool = False,
    extra_env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Unlock *vault_path* and run *command* with the decrypted variables injected.

    Args:
        vault_path: Path to the locked vault file.
        password: Password to decrypt the vault.
        command: Command + arguments to execute.
        override: If True, vault variables override existing env vars.
        extra_env: Additional variables merged after vault vars.

    Returns:
        CompletedProcess result from subprocess.run.
    """
    plaintext = unlock(vault_path, password)
    vault_vars = _parse_env(plaintext)

    child_env = os.environ.copy()
    if override:
        child_env.update(vault_vars)
    else:
        for k, v in vault_vars.items():
            child_env.setdefault(k, v)

    if extra_env:
        child_env.update(extra_env)

    return subprocess.run(command, env=child_env, capture_output=True, text=True)
