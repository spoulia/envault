"""CLI commands for renaming .env keys."""
from pathlib import Path

import click

from envault.env_rename import rename_keys


@click.group("rename")
def rename():
    """Rename keys in a .env file."""


@rename.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("-m", "--map", "mappings", multiple=True, metavar="OLD=NEW",
              required=True, help="Key rename mapping (repeatable).")
@click.option("-o", "--output", "dst", default=None, type=click.Path(path_type=Path),
              help="Output file (default: overwrite source).")
@click.option("--overwrite", is_flag=True, default=False,
              help="Allow overwriting an existing key with the new name.")
def run_cmd(src: Path, mappings: tuple[str, ...], dst: Path | None, overwrite: bool):
    """Rename keys in SRC .env file."""
    mapping: dict[str, str] = {}
    for m in mappings:
        if "=" not in m:
            raise click.BadParameter(f"Mapping must be OLD=NEW, got: {m}")
        old, _, new = m.partition("=")
        mapping[old.strip()] = new.strip()

    try:
        result = rename_keys(src, mapping, dst=dst, overwrite=overwrite)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for old, new in result.renamed:
        click.echo(f"Renamed: {old} -> {new}")
    for key in result.skipped:
        click.echo(f"Skipped (target exists): {key}")
    for key in result.not_found:
        click.echo(f"Not found: {key}")

    if not result.renamed:
        click.echo("No keys were renamed.")
