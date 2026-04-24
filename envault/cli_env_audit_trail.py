"""CLI commands for the per-key audit trail."""
from __future__ import annotations

import click
from pathlib import Path
from datetime import datetime

from envault.env_audit_trail import get_trail, clear_trail, _DEFAULT_TRAIL


@click.group("trail")
def trail_cmd() -> None:
    """Per-key change audit trail."""


@trail_cmd.command("show")
@click.option("--key", default=None, help="Filter by key name.")
@click.option("--source", default=None, help="Filter by source file.")
@click.option("--last", default=0, type=int, help="Show only the last N entries.")
@click.option(
    "--trail-file",
    default=str(_DEFAULT_TRAIL),
    show_default=True,
    help="Path to trail file.",
)
def show_cmd(
    key: str | None,
    source: str | None,
    last: int,
    trail_file: str,
) -> None:
    """Display audit trail entries."""
    result = get_trail(key=key, source=source, trail_file=Path(trail_file))
    entries = result.entries
    if last > 0:
        entries = entries[-last:]
    if not entries:
        click.echo("No trail entries found.")
        return
    for e in entries:
        ts = datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        old = e.old_value if e.old_value is not None else "<none>"
        new = e.new_value if e.new_value is not None else "<none>"
        click.echo(f"[{ts}] {e.action.upper():6s}  {e.key}  {old} -> {new}  ({e.source})")


@trail_cmd.command("clear")
@click.option(
    "--trail-file",
    default=str(_DEFAULT_TRAIL),
    show_default=True,
    help="Path to trail file.",
)
@click.confirmation_option(prompt="Clear all trail entries?")
def clear_cmd(trail_file: str) -> None:
    """Delete all audit trail entries."""
    clear_trail(Path(trail_file))
    click.echo("Audit trail cleared.")
