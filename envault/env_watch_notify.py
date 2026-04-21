"""env_watch_notify.py — Watch .env file for changes and trigger notifications/hooks.

Extends the basic watch functionality with configurable notification callbacks
(stdout, desktop notify, webhook) and integrates with the hooks system.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class WatchEvent:
    """Represents a single change event detected while watching a file."""
    path: str
    timestamp: float
    old_hash: str
    new_hash: str
    event_type: str = "changed"  # "changed" | "created" | "deleted"


@dataclass
class WatchSession:
    """Summary of a completed (or interrupted) watch session."""
    path: str
    events: List[WatchEvent] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None

    @property
    def event_count(self) -> int:  # noqa: D401
        return len(self.events)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _file_hash(path: Path) -> Optional[str]:
    """Return the SHA-256 hex digest of *path*, or None if the file is absent."""
    try:
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()
    except FileNotFoundError:
        return None


def _notify_stdout(event: WatchEvent) -> None:
    """Print a human-readable change notice to stdout."""
    ts = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
    print(f"[envault watch] {ts}  {event.event_type}: {event.path}")


def _notify_webhook(url: str, event: WatchEvent) -> None:
    """POST a JSON payload to *url* describing the change event."""
    try:
        import urllib.request  # stdlib — no extra deps

        payload = json.dumps({
            "path": event.path,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "old_hash": event.old_hash,
            "new_hash": event.new_hash,
        }).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)  # noqa: S310
    except Exception as exc:  # pragma: no cover
        print(f"[envault watch] webhook error: {exc}")


def _run_shell_hook(command: str, event: WatchEvent) -> None:
    """Execute *command* in a shell, passing event details as env variables."""
    env_extra = {
        "ENVAULT_EVENT": event.event_type,
        "ENVAULT_PATH": event.path,
        "ENVAULT_TIMESTAMP": str(event.timestamp),
    }
    import os
    merged = {**os.environ, **env_extra}
    subprocess.run(command, shell=True, env=merged)  # noqa: S602


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def watch_notify(
    path: str | Path,
    *,
    interval: float = 1.0,
    max_events: Optional[int] = None,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
    webhook_url: Optional[str] = None,
    shell_hook: Optional[str] = None,
    silent: bool = False,
) -> WatchSession:
    """Watch *path* for modifications and fire notification callbacks.

    Parameters
    ----------
    path:        File to watch.
    interval:    Polling interval in seconds.
    max_events:  Stop after this many change events (useful for testing).
    on_change:   Optional custom callback receiving a :class:`WatchEvent`.
    webhook_url: If set, POST a JSON payload to this URL on each change.
    shell_hook:  If set, run this shell command on each change.
    silent:      Suppress built-in stdout notifications.

    Returns
    -------
    :class:`WatchSession` describing the session once it ends.
    """
    target = Path(path)
    session = WatchSession(path=str(target))
    current_hash = _file_hash(target)

    try:
        while True:
            time.sleep(interval)
            new_hash = _file_hash(target)

            if new_hash == current_hash:
                continue

            event_type = (
                "created" if current_hash is None
                else "deleted" if new_hash is None
                else "changed"
            )
            event = WatchEvent(
                path=str(target),
                timestamp=time.time(),
                old_hash=current_hash or "",
                new_hash=new_hash or "",
                event_type=event_type,
            )
            session.events.append(event)
            current_hash = new_hash

            # Fire notifications
            if not silent:
                _notify_stdout(event)
            if on_change:
                on_change(event)
            if webhook_url:
                _notify_webhook(webhook_url, event)
            if shell_hook:
                _run_shell_hook(shell_hook, event)

            if max_events is not None and session.event_count >= max_events:
                break
    except KeyboardInterrupt:
        pass
    finally:
        session.ended_at = time.time()

    return session
