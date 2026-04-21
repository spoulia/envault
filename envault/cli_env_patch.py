"""CLI commands for patching .env files."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import click

from .env_patch import patch_file


@click.group("patch")
def patch_cmd() -> None:
    """Apply key-value patches to an .env file."""


@patch_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-s",
    "--set",
    "pairs",
    multiple=True,
    metavar="KEY=VALUE",
    help="Override KEY with VALUE (repeatable).",
)
@click.option(
    "-r",
    "--remove",
    "remove_keys",
    multiple=True,
    metavar="KEY",
    help="Remove KEY from the file (repeatable).",
)
@click.option(
    "--no-overwrite",
    is_flag=True,
    default=False,
    help="Skip keys that already exist.",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Write result to OUTPUT instead of modifying in place.",
)
def run_cmd(
    env_file: Path,
    pairs: Tuple[str, ...],
    remove_keys: Tuple[str, ...],
    no_overwrite: bool,
    output_path: Path | None,
) -> None:
    """Patch ENV_FILE with the supplied overrides and removals."""
    overrides: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair!r}")
        k, _, v = pair.partition("=")
        overrides[k.strip()] = v.strip()

    result = patch_file(
        env_file,
        overrides=overrides,
        remove_keys=list(remove_keys),
        overwrite=not no_overwrite,
        output_path=output_path,
    )

    if result.applied:
        click.echo(f"Applied  ({result.applied_count}): {', '.join(result.applied)}")
    if result.skipped:
        click.echo(f"Skipped  ({result.skipped_count}): {', '.join(result.skipped)}")
    if result.removed:
        click.echo(f"Removed  ({result.removed_count}): {', '.join(result.removed)}")
    if not (result.applied or result.skipped or result.removed):
        click.echo("Nothing to patch.")
