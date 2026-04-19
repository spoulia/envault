"""CLI commands for env_alias."""
import click
from pathlib import Path
from envault.env_alias import add_alias, remove_alias, list_aliases, resolve_aliases


@click.group()
def alias():
    """Manage key aliases for .env files."""


@alias.command("add")
@click.argument("alias_name")
@click.argument("target")
@click.option("--alias-file", default=".envault_aliases.json", show_default=True)
def add_cmd(alias_name, target, alias_file):
    """Add an alias ALIAS_NAME pointing to TARGET key."""
    try:
        add_alias(alias_name, target, Path(alias_file))
        click.echo(f"Alias '{alias_name}' -> '{target}' added.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)


@alias.command("remove")
@click.argument("alias_name")
@click.option("--alias-file", default=".envault_aliases.json", show_default=True)
def remove_cmd(alias_name, alias_file):
    """Remove an alias."""
    try:
        remove_alias(alias_name, Path(alias_file))
        click.echo(f"Alias '{alias_name}' removed.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)


@alias.command("list")
@click.option("--alias-file", default=".envault_aliases.json", show_default=True)
def list_cmd(alias_file):
    """List all registered aliases."""
    aliases = list_aliases(Path(alias_file))
    if not aliases:
        click.echo("No aliases defined.")
        return
    for a, t in aliases.items():
        click.echo(f"  {a} -> {t}")


@alias.command("resolve")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--alias-file", default=".envault_aliases.json", show_default=True)
def resolve_cmd(env_file, alias_file):
    """Resolve all aliases against ENV_FILE and print values."""
    results = resolve_aliases(Path(env_file), Path(alias_file))
    if not results:
        click.echo("No aliases to resolve.")
        return
    for r in results:
        val = r.resolved_value if r.resolved_value is not None else "<not found>"
        click.echo(f"  {r.alias} -> {r.target} = {val}")
