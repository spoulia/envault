"""CLI commands for copying keys between vaults."""
from pathlib import Path

import click

from envault.env_copy import copy_keys


@click.group("copy")
def copy():
    """Copy keys between vault files."""


@copy.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(path_type=Path))
@click.option("--src-password", prompt=True, hide_input=True, help="Source vault password.")
@click.option("--dst-password", prompt=True, hide_input=True, help="Destination vault password.")
@click.option("--key", "keys", multiple=True, help="Keys to copy (repeatable). Copies all if omitted.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def run_cmd(src, dst, src_password, dst_password, keys, overwrite):
    """Copy keys from SRC vault into DST vault."""
    try:
        result = copy_keys(
            src=src,
            src_password=src_password,
            dst=dst,
            dst_password=dst_password,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if result.copied:
        click.echo(f"Copied: {', '.join(result.copied)}")
    else:
        click.echo("No keys were copied.")

    if result.skipped:
        click.echo(f"Skipped: {', '.join(result.skipped)}")
