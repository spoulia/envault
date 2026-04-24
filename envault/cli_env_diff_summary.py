"""CLI commands for env-diff-summary – show a human-readable change summary
between two .env files."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_diff_summary import format_summary, summarise


@click.group("diff-summary")
def diff_summary_cmd() -> None:
    """Summarise changes between two .env files."""


@diff_summary_cmd.command("show")
@click.argument("before", type=click.Path(exists=True, path_type=Path))
@click.argument("after", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--no-mask",
    is_flag=True,
    default=False,
    help="Show actual values instead of masking them.",
)
@click.option(
    "--counts-only",
    is_flag=True,
    default=False,
    help="Print only the change counts, not the individual keys.",
)
def show_cmd(before: Path, after: Path, no_mask: bool, counts_only: bool) -> None:
    """Show a summary of differences between BEFORE and AFTER .env files."""
    try:
        result = summarise(before, after)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if counts_only:
        click.echo(
            f"added={result.total_added} "
            f"removed={result.total_removed} "
            f"changed={result.total_changed}"
        )
        return

    output = format_summary(result, mask_values=not no_mask)
    click.echo(output)

    if result.has_changes:
        raise SystemExit(0)
