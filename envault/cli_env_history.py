"""CLI commands for env change history."""
import click
from pathlib import Path
from datetime import datetime

from .env_history import get_history, clear_history, DEFAULT_HISTORY_FILE


@click.group("history")
def history():
    """View and manage .env change history."""


@history.command("show")
@click.option("--key", default=None, help="Filter by key name.")
@click.option("--last", default=None, type=int, help="Show last N entries.")
@click.option(
    "--file",
    "history_file",
    default=str(DEFAULT_HISTORY_FILE),
    show_default=True,
    help="History file path.",
)
def show_cmd(key, last, history_file):
    """Show change history."""
    result = get_history(key=key, last=last, history_file=Path(history_file))
    if result.count == 0:
        click.echo("No history entries found.")
        return
    for e in result.entries:
        ts = datetime.fromtimestamp(e.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        old = e.old_value if e.old_value is not None else "(none)"
        new = e.new_value if e.new_value is not None else "(none)"
        note = f"  # {e.note}" if e.note else ""
        click.echo(f"[{ts}] {e.action:8s} {e.key}: {old} -> {new}{note}")


@history.command("clear")
@click.option(
    "--file",
    "history_file",
    default=str(DEFAULT_HISTORY_FILE),
    show_default=True,
)
@click.confirmation_option(prompt="Clear all history?")
def clear_cmd(history_file):
    """Clear all history entries."""
    clear_history(history_file=Path(history_file))
    click.echo("History cleared.")
