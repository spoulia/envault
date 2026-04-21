"""CLI commands for env-flatten feature."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_flatten import flatten_env, format_flatten


@click.group("flatten")
def flatten_cmd() -> None:
    """Flatten nested JSON values in .env files into dotted keys."""


@flatten_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Write flattened output to this file instead of stdout.",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress summary output.")
def run_cmd(env_file: Path, output: Path | None, quiet: bool) -> None:
    """Flatten nested JSON values in ENV_FILE."""
    try:
        result = flatten_env(env_file)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    rendered = format_flatten(result)

    if output:
        output.write_text(rendered + "\n")
        if not quiet:
            click.echo(
                f"Flattened {result.flattened_count} key(s) "
                f"from '{env_file}' -> '{output}'."
            )
    else:
        click.echo(rendered)
        if not quiet:
            click.echo(
                f"\n# {result.flattened_count} key(s) total.",
                err=True,
            )
