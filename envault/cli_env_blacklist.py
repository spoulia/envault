"""CLI commands for env-blacklist feature."""
from __future__ import annotations

from pathlib import Path
from typing import List

import click

from envault.env_blacklist import blacklist_file, removed_count, kept_count


@click.group("blacklist")
def blacklist_cmd() -> None:
    """Remove blacklisted keys from .env files."""


@blacklist_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("-k", "--key", "keys", multiple=True, help="Exact key to remove.")
@click.option("-p", "--pattern", "patterns", multiple=True, help="Regex pattern to match keys for removal.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without writing.")
def run_cmd(
    env_file: Path,
    keys: List[str],
    patterns: List[str],
    dry_run: bool,
) -> None:
    """Remove keys matching KEY or PATTERN from ENV_FILE."""
    if not keys and not patterns:
        raise click.UsageError("Provide at least one --key or --pattern.")

    result = blacklist_file(
        env_file,
        keys=list(keys),
        patterns=list(patterns),
        dry_run=dry_run,
    )

    if dry_run:
        click.echo("[dry-run] Output preview:")
        click.echo(result.output)
    else:
        click.echo(
            f"Removed {removed_count(result)} key(s), kept {kept_count(result)} key(s) in {env_file}."
        )

    if result.removed:
        click.echo("Removed: " + ", ".join(result.removed))
    else:
        click.echo("No keys matched the blacklist.")
