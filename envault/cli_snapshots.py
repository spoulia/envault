"""CLI commands for vault snapshots."""
import click
from pathlib import Path

from envault.snapshots import (
    save_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
)


@click.group()
def snapshots():
    """Manage vault snapshots."""


@snapshots.command("save")
@click.argument("name")
@click.option("--vault", default=".env.vault", show_default=True, help="Vault file.")
@click.option("--desc", default="", help="Optional description.")
def save_cmd(name, vault, desc):
    """Save a named snapshot of the vault."""
    try:
        entry = save_snapshot(Path(vault), name, description=desc)
        click.echo(f"Snapshot '{entry['name']}' saved at {entry['created_at']}.")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@snapshots.command("restore")
@click.argument("name")
@click.option("--vault", default=".env.vault", show_default=True, help="Target vault file.")
def restore_cmd(name, vault):
    """Restore vault from a named snapshot."""
    try:
        restore_snapshot(name, Path(vault))
        click.echo(f"Vault restored from snapshot '{name}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)


@snapshots.command("delete")
@click.argument("name")
def delete_cmd(name):
    """Delete a named snapshot."""
    try:
        delete_snapshot(name)
        click.echo(f"Snapshot '{name}' deleted.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)


@snapshots.command("list")
def list_cmd():
    """List all saved snapshots."""
    items = list_snapshots()
    if not items:
        click.echo("No snapshots found.")
        return
    for s in items:
        desc = f" — {s['description']}" if s.get("description") else ""
        click.echo(f"  {s['name']}{desc}  [{s['created_at']}]")
