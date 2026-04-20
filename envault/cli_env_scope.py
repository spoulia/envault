"""CLI commands for env scope management."""
from __future__ import annotations

from pathlib import Path

import click

from .env_scope import assign_scope, get_scope, keys_for_scope, list_scopes, remove_scope


@click.group("scope")
def scope_cmd():
    """Tag .env keys with deployment scopes (dev/staging/prod)."""


@scope_cmd.command("add")
@click.argument("key")
@click.argument("scopes", nargs=-1, required=True)
@click.option("--file", "reg_file", default=".envault_scopes.json", show_default=True)
def add_cmd(key: str, scopes: tuple, reg_file: str) -> None:
    """Assign SCOPES to KEY."""
    try:
        result = assign_scope(key, list(scopes), path=Path(reg_file))
        click.echo(f"Assigned {result.scopes} to '{key}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@scope_cmd.command("remove")
@click.argument("key")
@click.argument("scopes", nargs=-1, required=True)
@click.option("--file", "reg_file", default=".envault_scopes.json", show_default=True)
def remove_cmd(key: str, scopes: tuple, reg_file: str) -> None:
    """Remove SCOPES from KEY."""
    result = remove_scope(key, list(scopes), path=Path(reg_file))
    click.echo(f"Remaining scopes for '{key}': {result.scopes or '(none)'}")


@scope_cmd.command("show")
@click.argument("key")
@click.option("--file", "reg_file", default=".envault_scopes.json", show_default=True)
def show_cmd(key: str, reg_file: str) -> None:
    """Show scopes for KEY."""
    result = get_scope(key, path=Path(reg_file))
    if result.scopes:
        click.echo(f"{key}: {', '.join(result.scopes)}")
    else:
        click.echo(f"'{key}' has no scopes assigned.")


@scope_cmd.command("list")
@click.option("--file", "reg_file", default=".envault_scopes.json", show_default=True)
def list_cmd(reg_file: str) -> None:
    """List all scope assignments."""
    registry = list_scopes(path=Path(reg_file))
    if not registry:
        click.echo("No scope assignments found.")
        return
    for key, scopes in sorted(registry.items()):
        click.echo(f"  {key}: {', '.join(scopes)}")


@scope_cmd.command("find")
@click.argument("scope")
@click.option("--file", "reg_file", default=".envault_scopes.json", show_default=True)
def find_cmd(scope: str, reg_file: str) -> None:
    """Find all keys tagged with SCOPE."""
    try:
        keys = keys_for_scope(scope, path=Path(reg_file))
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo(f"No keys tagged with scope '{scope}'.")
    else:
        for k in keys:
            click.echo(f"  {k}")
