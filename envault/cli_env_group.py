"""CLI commands for env key grouping."""
import click
from pathlib import Path
from .env_group import group_by_prefix, format_groups


@click.group("group")
def group_cmd():
    """Group .env keys by prefix."""


@group_cmd.command("show")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--prefix",
    "-p",
    multiple=True,
    help="Prefix(es) to group by. Auto-detected if omitted.",
)
@click.option(
    "--separator",
    "-s",
    default="_",
    show_default=True,
    help="Key segment separator.",
)
def show_cmd(env_file: Path, prefix: tuple, separator: str):
    """Display keys grouped by prefix."""
    prefixes = list(prefix) if prefix else None
    try:
        result = group_by_prefix(env_file, prefixes=prefixes, separator=separator)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not result.groups and not result.ungrouped:
        click.echo("No keys found.")
        return

    click.echo(format_groups(result))
    total = sum(len(v) for v in result.groups.values()) + len(result.ungrouped)
    click.echo(f"\n{total} key(s) across {len(result.groups)} group(s).")
