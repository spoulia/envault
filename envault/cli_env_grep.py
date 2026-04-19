"""CLI commands for env-grep feature."""
import click
from pathlib import Path
from .env_grep import grep_files, format_grep


@click.group("grep")
def grep_cmd():
    """Search env files using regex patterns."""


@grep_cmd.command("run")
@click.argument("pattern")
@click.argument("files", nargs=-1, required=True, type=click.Path())
@click.option("--values/--no-values", default=True, show_default=True,
              help="Search within values.")
@click.option("--keys/--no-keys", default=True, show_default=True,
              help="Search within keys.")
@click.option("-i", "--ignore-case", is_flag=True, default=False,
              help="Case-insensitive matching.")
@click.option("--show-values", is_flag=True, default=False,
              help="Display matched values in output.")
def run_cmd(pattern, files, values, keys, ignore_case, show_values):
    """Search FILES for keys/values matching PATTERN."""
    paths = [Path(f) for f in files]
    try:
        result = grep_files(
            paths,
            pattern,
            search_values=values,
            search_keys=keys,
            ignore_case=ignore_case,
        )
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_grep(result, show_values=show_values))
    if result.match_count:
        click.echo(
            f"\n{result.match_count} match(es) across {result.files_searched} file(s)."
        )
