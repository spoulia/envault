"""CLI commands for env-supersede."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_supersede import supersede


@click.group("supersede")
def supersede_cmd() -> None:
    """Supersede target .env keys with values from a source file."""


@supersede_cmd.command("run")
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--key", "keys", multiple=True, help="Specific keys to supersede.")
@click.option(
    "--no-add",
    "add_missing",
    is_flag=True,
    default=True,
    flag_value=False,
    help="Do not add keys absent from target.",
)
@click.option(
    "--no-overwrite",
    "overwrite",
    is_flag=True,
    default=True,
    flag_value=False,
    help="Skip keys that already exist in target.",
)
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes only.")
def run_cmd(
    source: Path,
    target: Path,
    keys: tuple,
    add_missing: bool,
    overwrite: bool,
    dry_run: bool,
) -> None:
    """Apply SOURCE values into TARGET."""
    try:
        result = supersede(
            source,
            target,
            keys=list(keys) if keys else None,
            add_missing=add_missing,
            overwrite=overwrite,
            dry_run=dry_run,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    prefix = "[dry-run] " if dry_run else ""
    if result.applied:
        click.echo(f"{prefix}Updated {result.applied_count} key(s): {', '.join(result.applied)}")
    if result.added:
        click.echo(f"{prefix}Added {result.added_count} key(s): {', '.join(result.added)}")
    if result.skipped:
        click.echo(f"Skipped {result.skipped_count} key(s): {', '.join(result.skipped)}")
    if not result.applied and not result.added:
        click.echo("No changes applied.")
