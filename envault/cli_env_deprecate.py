"""CLI commands for managing deprecated .env keys."""
import click
from pathlib import Path

from envault.env_deprecate import add_deprecation, remove_deprecation, list_deprecations, scan_file


@click.group("deprecate")
def deprecate_cmd():
    """Manage and scan for deprecated .env keys."""


@deprecate_cmd.command("add")
@click.argument("key")
@click.option("--reason", required=True, help="Why this key is deprecated.")
@click.option("--replacement", default=None, help="Suggested replacement key.")
def add_cmd(key: str, reason: str, replacement):
    """Mark a key as deprecated."""
    try:
        add_deprecation(key, reason, replacement)
        click.echo(f"Marked '{key}' as deprecated.")
        if replacement:
            click.echo(f"  Replacement: {replacement}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)


@deprecate_cmd.command("remove")
@click.argument("key")
def remove_cmd(key: str):
    """Remove a key from the deprecation registry."""
    try:
        remove_deprecation(key)
        click.echo(f"Removed '{key}' from deprecation registry.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)


@deprecate_cmd.command("list")
def list_cmd():
    """List all deprecated keys."""
    entries = list_deprecations()
    if not entries:
        click.echo("No deprecated keys registered.")
        return
    for entry in entries:
        line = f"  {entry.key}: {entry.reason}"
        if entry.replacement:
            line += f" (use '{entry.replacement}' instead)"
        click.echo(line)


@deprecate_cmd.command("scan")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
def scan_cmd(env_file: Path):
    """Scan an .env file for deprecated keys."""
    result = scan_file(env_file)
    if not result.has_deprecated:
        click.echo("No deprecated keys found.")
        return
    click.echo(f"Found {len(result.found)} deprecated key(s):")
    for entry in result.found:
        line = f"  [DEPRECATED] {entry.key} — {entry.reason}"
        if entry.replacement:
            line += f" → use '{entry.replacement}'"
        click.echo(line)
