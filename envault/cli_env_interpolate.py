"""CLI commands for env-variable interpolation."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_interpolate import format_interpolate, has_unresolved, interpolate_file


@click.group("interpolate")
def interpolate_cmd() -> None:
    """Interpolate ${VAR} references inside a .env file."""


@interpolate_cmd.command("show")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--context",
    "-c",
    multiple=True,
    metavar="KEY=VALUE",
    help="Extra KEY=VALUE pairs added to the resolution context.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with non-zero status when unresolved references remain.",
)
def show_cmd(env_file: Path, context: tuple[str, ...], strict: bool) -> None:
    """Print the interpolated contents of ENV_FILE."""
    extra: dict[str, str] = {}
    for item in context:
        if "=" not in item:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {item}")
        k, _, v = item.partition("=")
        extra[k.strip()] = v.strip()

    try:
        result = interpolate_file(env_file, extra_context=extra or None)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_interpolate(result))

    if result.unresolved:
        click.echo(
            f"\nWarning: {len(result.unresolved)} unresolved reference(s): "
            + ", ".join(result.unresolved),
            err=True,
        )
        if strict:
            raise SystemExit(1)
