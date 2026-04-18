"""Tests for envault.watch."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.watch import watch
from envault.vault import unlock


PASSWORD = "watchpass"
ENV_CONTENT_A = "KEY=alpha\nFOO=bar\n"
ENV_CONTENT_B = "KEY=beta\nFOO=baz\nNEW=1\n"


@pytest.fixture()
def env_file(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text(ENV_CONTENT_A)
    return f


@pytest.fixture()
def vault_file(tmp_path: Path):
    return tmp_path / ".env.vault"


def test_watch_initial_lock_creates_vault(env_file, vault_file):
    """watch() should lock the file immediately on start."""
    watch(env_file, vault_file, PASSWORD, interval=0, max_iterations=0)
    assert vault_file.exists()


def test_watch_initial_lock_is_valid(env_file, vault_file):
    watch(env_file, vault_file, PASSWORD, interval=0, max_iterations=0)
    result = unlock(vault_file, PASSWORD)
    assert "KEY=alpha" in result


def test_watch_relocks_on_change(env_file, vault_file):
    changed: list[Path] = []

    def _on_change(p: Path):
        changed.append(p)

    # Run one iteration; mutate the file before sleeping by using interval=0
    # We monkey-patch time.sleep to avoid actual delays.
    import envault.watch as w_mod
    original_sleep = w_mod.time.sleep

    call_count = 0

    def fake_sleep(_):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            env_file.write_text(ENV_CONTENT_B)

    w_mod.time.sleep = fake_sleep
    try:
        watch(env_file, vault_file, PASSWORD, interval=0, max_iterations=1, on_change=_on_change)
    finally:
        w_mod.time.sleep = original_sleep

    assert len(changed) == 1
    result = unlock(vault_file, PASSWORD)
    assert "KEY=beta" in result


def test_watch_no_change_does_not_callback(env_file, vault_file):
    changed: list[Path] = []
    import envault.watch as w_mod
    w_mod.time.sleep = lambda _: None
    try:
        watch(env_file, vault_file, PASSWORD, interval=0, max_iterations=3, on_change=lambda p: changed.append(p))
    finally:
        import time as _t
        w_mod.time.sleep = _t.sleep
    assert changed == []


def test_watch_missing_file_raises(tmp_path, vault_file):
    with pytest.raises(FileNotFoundError):
        watch(tmp_path / "nonexistent.env", vault_file, PASSWORD, interval=0, max_iterations=0)
