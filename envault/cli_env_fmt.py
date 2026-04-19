"""CLI commands for env-fmt (format .env files)."""
import click
from pathlib import Path

from envault.env_fmt import fmt_file


@click.group("fmt")
def fmt():
    """Format .env files for consistency."""


@fmt.command("check")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
def check_cmd(env_file: Path):
    """Check a .env file for formatting issues without modifying it."""
    result = fmt_file(env_file, write=False)
    if not result.changes:
        click.echo(f"{env_file}: already formatted")
        return
    click.echo(f"{env_file}: {result.changed_count} line(s) would be reformatted")
    for lineno, before, after in result.changes:
        click.echo(f"  line {lineno}:")
        click.echo(f"    - {before}")
        click.echo(f"    + {after}")
    raise SystemExit(1)


@fmt.command("fix")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
def fix_cmd(env_file: Path):
    """Reformat a .env file in-place."""
    result = fmt_file(env_file, write=True)
    if result.written:
        click.echo(f"{env_file}: reformatted {result.changed_count} line(s)")
    else:
        click.echo(f"{env_file}: already formatted")
