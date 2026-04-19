"""CLI commands for env-trim feature."""
import click
from pathlib import Path

from envault.env_trim import trim_file


@click.group("trim")
def trim():
    """Trim duplicate keys from .env files."""


@trim.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, default=False, help="Preview without modifying.")
def run_cmd(env_file: Path, dry_run: bool):
    """Remove duplicate keys from ENV_FILE."""
    result = trim_file(env_file, dry_run=dry_run)

    if result.removed_count == 0:
        click.echo("No duplicates found.")
        return

    for key in result.removed:
        prefix = "[dry-run] " if dry_run else ""
        click.echo(f"{prefix}Removed duplicate: {key}")

    action = "Would remove" if dry_run else "Removed"
    click.echo(f"{action} {result.removed_count} duplicate key(s). Kept {result.kept_count} key(s).")
