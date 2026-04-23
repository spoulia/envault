"""CLI commands for checking required env keys."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.env_required import check_required, has_issues


@click.group("required")
def required_cmd():
    """Check that required keys are present in an env file."""


@required_cmd.command("check")
@click.argument("env_file", type=click.Path(exists=False))
@click.option("-k", "--key", "keys", multiple=True, required=True, help="Required key name (repeatable).")
@click.option("--allow-empty", is_flag=True, default=False, help="Allow keys to be present but empty.")
def check_cmd(env_file: str, keys: tuple, allow_empty: bool):
    """Check that KEY(s) are present (and non-empty) in ENV_FILE."""
    result = check_required(Path(env_file), list(keys), allow_empty=allow_empty)

    if not has_issues(result):
        click.echo(f"OK  All {len(result.checked)} required key(s) are present.")
        return

    for issue in result.issues:
        if issue.reason == "missing":
            click.echo(f"MISSING  {issue.key}", err=True)
        else:
            click.echo(f"EMPTY    {issue.key}", err=True)

    click.echo(
        f"\n{len(result.issues)} issue(s) found in '{env_file}'.",
        err=True,
    )
    sys.exit(1)
