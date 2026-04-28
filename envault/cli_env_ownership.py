"""cli_env_ownership.py – CLI commands for key ownership management."""
import click
from pathlib import Path

from envault.env_ownership import (
    assign_owner,
    update_owner,
    remove_owner,
    get_ownership,
    _DEFAULT_REGISTRY,
)


@click.group("ownership")
def ownership_cmd():
    """Manage key ownership metadata."""


@ownership_cmd.command("assign")
@click.argument("key")
@click.argument("owner")
@click.option("--team", default=None, help="Team responsible for this key.")
@click.option("--notes", default=None, help="Optional notes.")
@click.option("--registry", default=str(_DEFAULT_REGISTRY), show_default=True)
def assign_cmd(key, owner, team, notes, registry):
    """Assign an owner to KEY."""
    try:
        entry = assign_owner(key, owner, team=team, notes=notes, registry=Path(registry))
        click.echo(f"Assigned '{entry.owner}' as owner of '{entry.key}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ownership_cmd.command("update")
@click.argument("key")
@click.argument("owner")
@click.option("--team", default=None)
@click.option("--notes", default=None)
@click.option("--registry", default=str(_DEFAULT_REGISTRY), show_default=True)
def update_cmd(key, owner, team, notes, registry):
    """Update the owner of KEY."""
    entry = update_owner(key, owner, team=team, notes=notes, registry=Path(registry))
    click.echo(f"Updated owner of '{entry.key}' to '{entry.owner}'.")


@ownership_cmd.command("remove")
@click.argument("key")
@click.option("--registry", default=str(_DEFAULT_REGISTRY), show_default=True)
def remove_cmd(key, registry):
    """Remove ownership record for KEY."""
    removed = remove_owner(key, registry=Path(registry))
    if removed:
        click.echo(f"Removed ownership record for '{key}'.")
    else:
        click.echo(f"No ownership record found for '{key}'.")


@ownership_cmd.command("list")
@click.option("--owner", default=None, help="Filter by owner name.")
@click.option("--team", default=None, help="Filter by team name.")
@click.option("--registry", default=str(_DEFAULT_REGISTRY), show_default=True)
def list_cmd(owner, team, registry):
    """List all ownership records."""
    result = get_ownership(registry=Path(registry))
    entries = result.entries
    if owner:
        entries = result.by_owner(owner)
    elif team:
        entries = result.by_team(team)
    if not entries:
        click.echo("No ownership records found.")
        return
    for e in entries:
        parts = [f"{e.key} -> {e.owner}"]
        if e.team:
            parts.append(f"[team: {e.team}]")
        if e.notes:
            parts.append(f"# {e.notes}")
        click.echo("  ".join(parts))
