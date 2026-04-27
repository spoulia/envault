"""CLI commands for env-reorder feature."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_reorder import reorder_file


@click.group("reorder")
def reorder_cmd() -> None:
    """Reorder keys in a .env file."""


@reorder_cmd.command("run")
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--key",
    "-k",
    "keys",
    multiple=True,
    required=True,
    help="Key name in desired order (repeat for multiple).",
)
@click.option(
    "--output",
    "-o",
    "output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file (defaults to SOURCE).",
)
@click.option(
    "--drop-unmatched",
    is_flag=True,
    default=False,
    help="Drop keys not listed in --key instead of appending them.",
)
def run_cmd(
    source: Path,
    keys: tuple,
    output: Path | None,
    drop_unmatched: bool,
) -> None:
    """Reorder keys in SOURCE according to the --key order."""
    result = reorder_file(
        source=source,
        order=list(keys),
        output=output,
        append_unmatched=not drop_unmatched,
    )
    click.echo(f"Reordered {len(result.ordered_keys)} key(s) in {result.output}")
    if result.unmatched_keys and not drop_unmatched:
        click.echo(
            f"Appended {len(result.unmatched_keys)} unmatched key(s): "
            + ", ".join(result.unmatched_keys)
        )
    elif result.unmatched_keys and drop_unmatched:
        click.echo(
            f"Dropped {len(result.unmatched_keys)} unmatched key(s): "
            + ", ".join(result.unmatched_keys)
        )
