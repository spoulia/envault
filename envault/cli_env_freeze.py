"""CLI commands for env freeze / drift detection."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_freeze import freeze, check_drift


@click.group("freeze")
def freeze_cmd() -> None:
    """Freeze env values and detect drift."""


@freeze_cmd.command("snap")
@click.argument("env_file", default=".env")
@click.option("--output", "-o", default=None, help="Path to write freeze file.")
def snap_cmd(env_file: str, output: str | None) -> None:
    """Snapshot current env values into a freeze file."""
    try:
        result = freeze(
            Path(env_file),
            Path(output) if output else None,
        )
        click.echo(f"Frozen {result.keys_frozen} keys from '{result.source}' → '{result.freeze_file}'")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@freeze_cmd.command("drift")
@click.argument("env_file", default=".env")
@click.option("--freeze-file", "-f", default=None, help="Path to freeze file.")
@click.option("--strict", is_flag=True, help="Exit non-zero if drift is detected.")
def drift_cmd(env_file: str, freeze_file: str | None, strict: bool) -> None:
    """Check whether the env file has drifted from its frozen snapshot."""
    try:
        result = check_drift(
            Path(env_file),
            Path(freeze_file) if freeze_file else None,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not result.has_drift:
        click.echo("No drift detected.")
        return

    click.echo(f"Drift detected in '{result.source}':")
    for issue in result.issues:
        if issue.kind == "changed":
            click.echo(f"  ~ {issue.key}  (was: {issue.frozen_value!r}  now: {issue.current_value!r})")
        elif issue.kind == "added":
            click.echo(f"  + {issue.key}  (new value: {issue.current_value!r})")
        else:
            click.echo(f"  - {issue.key}  (removed, was: {issue.frozen_value!r})")

    if strict:
        raise SystemExit(1)
