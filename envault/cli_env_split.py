"""CLI commands for splitting .env files."""
import click
from pathlib import Path
from envault.env_split import split_by_prefix


@click.group("split")
def split_cmd():
    """Split a .env file into multiple files by prefix."""


@split_cmd.command("run")
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option("-p", "--prefix", "prefixes", multiple=True, required=True,
              help="Prefix to split on (repeatable).")
@click.option("-o", "--output-dir", type=click.Path(path_type=Path),
              default=Path("."), show_default=True,
              help="Directory to write split files into.")
@click.option("--remainder", default=None,
              help="Filename for unmatched keys (omitted if not set).")
def run_cmd(source: Path, prefixes: tuple, output_dir: Path, remainder: str):
    """Split SOURCE .env by PREFIX into OUTPUT_DIR."""
    if not prefixes:
        click.echo("Error: at least one --prefix is required.", err=True)
        raise SystemExit(1)

    result = split_by_prefix(
        source=source,
        output_dir=output_dir,
        prefixes=list(prefixes),
        remainder_file=remainder,
    )

    if result.files_written:
        for f in result.files_written:
            click.echo(f"  wrote {f}")
        click.echo(f"Split {result.keys_split} key(s) into {len(result.files_written)} file(s).")
    else:
        click.echo("No keys matched the given prefixes. Nothing written.")

    if result.keys_unmatched and not remainder:
        click.echo(
            f"  {result.keys_unmatched} unmatched key(s) were not written "
            "(use --remainder to capture them)."
        )
