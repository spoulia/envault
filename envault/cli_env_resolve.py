"""CLI commands for resolving variable references in .env files."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_resolve import has_issues, resolve_file


@click.group("resolve")
def resolve_cmd() -> None:
    """Resolve ${VAR} references inside a .env file."""


@resolve_cmd.command("show")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--only-issues", is_flag=True, default=False,
              help="Only print keys with unresolved references or cycles.")
def show_cmd(env_file: Path, only_issues: bool) -> None:
    """Print resolved values for all keys in ENV_FILE."""
    result = resolve_file(env_file)

    if only_issues:
        if not has_issues(result):
            click.echo("No issues found.")
            return
        for key in result.unresolved:
            click.echo(f"UNRESOLVED  {key}={result.resolved[key]}")
        for key in result.cycles:
            click.echo(f"CYCLE       {key}")
        raise SystemExit(1)

    for key, value in result.resolved.items():
        tag = ""
        if key in result.cycles:
            tag = "  [cycle]"
        elif key in result.unresolved:
            tag = "  [unresolved]"
        click.echo(f"{key}={value}{tag}")

    if has_issues(result):
        raise SystemExit(1)
