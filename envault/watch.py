"""Watch a .env file for changes and re-lock automatically."""
from __future__ import annotations

import time
import hashlib
import os
from pathlib import Path
from typing import Callable, Optional

from envault.vault import lock
from envault.audit import record


def _file_hash(path: Path) -> str:
    """Return MD5 hex digest of file contents."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def watch(
    env_path: Path,
    vault_path: Path,
    password: str,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[Path], None]] = None,
) -> None:
    """Poll *env_path* and re-lock into *vault_path* whenever it changes.

    Parameters
    ----------
    env_path:       Path to the plain-text .env file being watched.
    vault_path:     Destination vault file.
    password:       Encryption password.
    interval:       Polling interval in seconds.
    max_iterations: Stop after this many polls (useful for testing).
    on_change:      Optional callback invoked with *env_path* after each lock.
    """
    if not env_path.exists():
        raise FileNotFoundError(f"Watch target not found: {env_path}")

    last_hash = _file_hash(env_path)
    # Perform an initial lock so the vault is always up-to-date on start.
    lock(env_path, vault_path, password)
    record("watch", {"event": "initial_lock", "file": str(env_path)})

    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        iterations += 1

        if not env_path.exists():
            record("watch", {"event": "file_removed", "file": str(env_path)})
            break

        current_hash = _file_hash(env_path)
        if current_hash != last_hash:
            lock(env_path, vault_path, password)
            record("watch", {"event": "re_locked", "file": str(env_path)})
            last_hash = current_hash
            if on_change:
                on_change(env_path)
