"""CLI commands for env-cross-check feature."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_cross_check import cross_check, format_cross_check, has_issues


@click.group("cross-check")
def cross_check_cmd() -> None:
    """Cross-check keys between two .env files."""


@cross_check_cmd.command("run")
@click.argument("reference", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(path_type=Path))
@click.option(
    "--allow-empty",
    is_flag=True,
    default=False,
    help="Allow empty values in target (only check presence).",
)
@click.option(
    "--key",
    "keys",
    multiple=True,
    metavar="KEY",
    help="Restrict check to specific key(s). Repeatable.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status when issues are found.",
)
def run_cmd(
    reference: Path,
    target: Path,
    allow_empty: bool,
    keys: tuple,
    strict: bool,
) -> None:
    """Cross-check REFERENCE keys against TARGET .env file."""
    try:
        result = cross_check(
            reference=reference,
            target=target,
            allow_empty=allow_empty,
            keys=list(keys) if keys else None,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_cross_check(result))

    if strict and has_issues(result):
        raise SystemExit(1)
