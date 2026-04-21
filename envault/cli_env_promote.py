"""CLI commands for promoting env keys between files."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_promote import promote_keys


@click.group("promote")
def promote_cmd() -> None:
    """Promote keys from one .env file to another."""


@promote_cmd.command("run")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("dst", type=click.Path(dir_okay=False, path_type=Path))
@click.option("-k", "--key", "keys", multiple=True, help="Key(s) to promote (default: all).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def run_cmd(src: Path, dst: Path, keys: tuple, overwrite: bool) -> None:
    """Promote keys from SRC into DST."""
    if not dst.exists():
        click.echo(f"Error: destination file '{dst}' does not exist.", err=True)
        raise SystemExit(1)

    try:
        result = promote_keys(
            src=src,
            dst=dst,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if result.promoted:
        click.echo(f"Promoted {result.promoted_count} key(s) from '{src}' to '{dst}':")
        for k in result.promoted:
            click.echo(f"  + {k}")
    else:
        click.echo("No keys were promoted.")

    if result.skipped:
        click.echo(f"Skipped {result.skipped_count} key(s): {', '.join(result.skipped)}")
