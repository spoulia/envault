"""CLI commands for env namespace management."""
import click
from pathlib import Path

from envault.env_namespace import add_namespace, strip_namespace, list_namespaces


@click.group("namespace")
def namespace_cmd():
    """Add, strip, or inspect key namespaces in .env files."""


@namespace_cmd.command("add")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.argument("prefix")
def add_cmd(file: Path, prefix: str):
    """Prepend PREFIX to all keys that don't already have it."""
    result = add_namespace(file, prefix)
    if result.affected_count == 0:
        click.echo("No keys were modified (all already have the prefix).")
    else:
        click.echo(f"Prefixed {result.affected_count} key(s) with '{prefix}':")
        for k in result.affected:
            click.echo(f"  {k} -> {prefix}{k}")
    if result.skipped_count:
        click.echo(f"Skipped {result.skipped_count} key(s) (already prefixed).")


@namespace_cmd.command("strip")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.argument("prefix")
def strip_cmd(file: Path, prefix: str):
    """Remove PREFIX from all keys that start with it."""
    result = strip_namespace(file, prefix)
    if result.affected_count == 0:
        click.echo(f"No keys found with prefix '{prefix}'.")
    else:
        click.echo(f"Stripped prefix from {result.affected_count} key(s):")
        for k in result.affected:
            click.echo(f"  {k} -> {k[len(prefix):]}")
    if result.skipped_count:
        click.echo(f"Skipped {result.skipped_count} key(s) (no matching prefix).")


@namespace_cmd.command("list")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def list_cmd(file: Path):
    """Show detected namespaces (prefixes) in FILE."""
    buckets = list_namespaces(file)
    if not buckets:
        click.echo("No keys found.")
        return
    for prefix, keys in sorted(buckets.items()):
        click.echo(f"[{prefix}] ({len(keys)} key(s))")
        for k in keys:
            click.echo(f"  {k}")
