"""CLI commands for audit log inspection."""

import json
import click
from envault.audit import get_log, clear_log, AUDIT_LOG_FILE


@click.group()
def audit():
    """Manage the envault audit log."""
    pass


@audit.command("show")
@click.option("--log", default=AUDIT_LOG_FILE, help="Path to audit log file.")
@click.option("--last", default=None, type=int, help="Show last N entries.")
def show_cmd(log, last):
    """Display audit log entries."""
    entries = get_log(log_path=log)
    if not entries:
        click.echo("No audit log entries found.")
        return
    if last is not None:
        entries = entries[-last:]
    for entry in entries:
        click.echo(
            f"[{entry['timestamp']}] {entry['user']} — {entry['action']}"
            + (f" | {entry['details']}" if entry["details"] else "")
        )


@audit.command("clear")
@click.option("--log", default=AUDIT_LOG_FILE, help="Path to audit log file.")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_cmd(log):
    """Clear all audit log entries."""
    clear_log(log_path=log)
    click.echo("Audit log cleared.")


@audit.command("export")
@click.argument("output")
@click.option("--log", default=AUDIT_LOG_FILE, help="Path to audit log file.")
def export_cmd(output, log):
    """Export audit log to a JSON file."""
    entries = get_log(log_path=log)
    with open(output, "w") as f:
        json.dump(entries, f, indent=2)
    click.echo(f"Exported {len(entries)} entries to {output}.")
