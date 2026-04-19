"""Pre/post hooks for vault operations."""
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

HOOKS_FILE = Path(".envault_hooks.json")

VALID_EVENTS = ["pre-lock", "post-lock", "pre-unlock", "post-unlock"]


def _load_hooks() -> dict:
    if not HOOKS_FILE.exists():
        return {}
    with open(HOOKS_FILE) as f:
        return json.load(f)


def _save_hooks(hooks: dict) -> None:
    with open(HOOKS_FILE, "w") as f:
        json.dump(hooks, f, indent=2)


def add_hook(event: str, command: str) -> None:
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Valid events: {VALID_EVENTS}")
    hooks = _load_hooks()
    hooks.setdefault(event, [])
    if command in hooks[event]:
        raise ValueError(f"Hook '{command}' already registered for event '{event}'")
    hooks[event].append(command)
    _save_hooks(hooks)


def remove_hook(event: str, command: str) -> None:
    hooks = _load_hooks()
    if event not in hooks or command not in hooks[event]:
        raise KeyError(f"Hook '{command}' not found for event '{event}'")
    hooks[event].remove(command)
    if not hooks[event]:
        del hooks[event]
    _save_hooks(hooks)


def get_hooks(event: str) -> list:
    return _load_hooks().get(event, [])


def list_all_hooks() -> dict:
    """Return all registered hooks grouped by event.

    Only includes events that have at least one hook registered.
    """
    return {event: cmds for event, cmds in _load_hooks().items() if cmds}


def run_hooks(event: str, env: Optional[dict] = None) -> list:
    """Run all hooks for an event. Returns list of (command, returncode) tuples."""
    results = []
    merged_env = {**os.environ, **(env or {})}
    for cmd in get_hooks(event):
        result = subprocess.run(cmd, shell=True, env=merged_env)
        results.append((cmd, result.returncode))
    return results
