"""CLI commands for env-chunk feature."""
import click
from pathlib import Path
from envault.env_chunk import chunk_file, format_chunk


@click.group("chunk")
def chunk_cmd():
    """Split a .env file into fixed-size chunks."""


@chunk_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--size", default=10, show_default=True, help="Keys per chunk.")
@click.option("--index", default=None, type=int, help="Show only this chunk (0-based).")
def run_cmd(env_file: Path, size: int, index):
    """Chunk ENV_FILE into groups of SIZE keys."""
    try:
        result = chunk_file(env_file, chunk_size=size)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(
        f"Total keys: {result.total_keys} | "
        f"Chunks: {result.chunk_count} | "
        f"Chunk size: {result.chunk_size}"
    )

    if index is not None:
        if index < 0 or index >= result.chunk_count:
            click.echo(f"Error: chunk index {index} out of range (0-{result.chunk_count - 1})", err=True)
            raise SystemExit(1)
        click.echo(format_chunk(result.chunks[index], index))
    else:
        for i, chunk in enumerate(result.chunks):
            click.echo(format_chunk(chunk, i))
