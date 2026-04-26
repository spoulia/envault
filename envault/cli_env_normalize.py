"""CLI commands for env-normalize."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_normalize import normalize_file


@click.group("normalize")
def normalize_cmd() -> None:
    """Normalize .env file keys and values."""


@normalize_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing.")
def run_cmd(env_file: Path, dry_run: bool) -> None:
    """Normalize ENV_FILE in place (or preview with --dry-run)."""
    result = normalize_file(env_file, dry_run=dry_run)

    if not result.changed:
        click.echo("Already normalized — no changes needed.")
        return

    label = "Would change" if dry_run else "Changed"
    click.echo(f"{label} {result.changed_count} line(s) in {env_file}:")
    for lineno, before, after in result.changes:
        click.echo(f"  line {lineno}:")
        click.echo(f"    - {before}")
        click.echo(f"    + {after}")

    if dry_run:
        click.echo("Dry-run mode — file not modified.")
