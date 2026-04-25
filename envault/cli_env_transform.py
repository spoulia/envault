"""CLI commands for env-transform (apply value transformations)."""
from __future__ import annotations

from pathlib import Path

import click

from .env_transform import changed_count, skipped_count, transform_env


@click.group("transform")
def transform_cmd() -> None:
    """Apply value transformations to a .env file."""


@transform_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--operation", required=True,
              help="Transformation: uppercase|lowercase|strip|strip_quotes|replace:<old>:<new>")
@click.option("-k", "--key", "keys", multiple=True,
              help="Limit to specific key(s). Repeat for multiple.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Preview changes without writing to disk.")
def run_cmd(env_file: Path, operation: str, keys: tuple, dry_run: bool) -> None:
    """Transform values in ENV_FILE using OPERATION."""
    try:
        result = transform_env(
            env_file,
            operation,
            keys=list(keys) if keys else None,
            write=not dry_run,
        )
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if dry_run:
        click.echo("[dry-run] no changes written")

    if changed_count(result) == 0:
        click.echo("No values changed.")
        return

    click.echo(f"Changed {changed_count(result)} key(s):")
    for k in result.changed_keys:
        click.echo(f"  {k} -> {result.transformed[k]}")

    if skipped_count(result):
        click.echo(f"Skipped {skipped_count(result)} key(s) (already matching or excluded).")
