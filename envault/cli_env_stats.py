"""CLI commands for env-stats."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_stats import compute_stats


@click.group()
def stats():
    """Show statistics about a .env file."""


@stats.command("show")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--prefixes", is_flag=True, default=False, help="Show key prefix breakdown.")
def show_cmd(env_file: Path, prefixes: bool):
    """Display statistics for ENV_FILE."""
    try:
        r = compute_stats(env_file)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Total keys       : {r.total_keys}")
    click.echo(f"Empty values     : {r.empty_values}")
    click.echo(f"Placeholders     : {r.placeholder_values}")
    click.echo(f"Comment lines    : {r.comment_lines}")
    click.echo(f"Blank lines      : {r.blank_lines}")

    if r.duplicate_keys:
        click.echo(f"Duplicate keys   : {', '.join(r.duplicate_keys)}")
    else:
        click.echo("Duplicate keys   : none")

    if prefixes and r.prefix_counts:
        click.echo("\nPrefix breakdown:")
        for prefix, count in sorted(r.prefix_counts.items()):
            click.echo(f"  {prefix}: {count}")
