"""Audit log for envault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_FILE = ".envault_audit.json"


def _load_log(log_path: str) -> list:
    path = Path(log_path)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_log(entries: list, log_path: str) -> None:
    with open(log_path, "w") as f:
        json.dump(entries, f, indent=2)


def record(action: str, details: dict = None, log_path: str = AUDIT_LOG_FILE) -> dict:
    """Append an audit entry and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user": os.environ.get("USER", "unknown"),
        "details": details or {},
    }
    entries = _load_log(log_path)
    entries.append(entry)
    _save_log(entries, log_path)
    return entry


def get_log(log_path: str = AUDIT_LOG_FILE) -> list:
    """Return all audit log entries."""
    return _load_log(log_path)


def clear_log(log_path: str = AUDIT_LOG_FILE) -> None:
    """Clear the audit log."""
    _save_log([], log_path)
