"""CLI commands for filtering .env keys."""
import click
from pathlib import Path

from .env_filter import filter_keys


@click.group("filter")
def filter_cmd():
    """Filter keys in a .env file."""


@filter_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--key", "keys", multiple=True, help="Exact key name(s) to match.")
@click.option("--prefix", default=None, help="Keep keys starting with prefix.")
@click.option("--pattern", default=None, help="Glob pattern for key names.")
@click.option("--exclude", is_flag=True, default=False, help="Remove matching keys instead of keeping.")
@click.option("--write", is_flag=True, default=False, help="Write result back to file.")
def run_cmd(env_file: Path, keys, prefix, pattern, exclude, write):
    """Filter keys from ENV_FILE by key name, prefix, or glob pattern."""
    try:
        result = filter_keys(
            env_file,
            keys=list(keys) if keys else None,
            prefix=prefix,
            pattern=pattern,
            exclude=exclude,
            write=write,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for k, v in result.kept.items():
        click.echo(f"{k}={v}")

    if write:
        click.echo(f"\nWrote {result.kept_count} keys ({result.removed_count} removed).", err=True)
    else:
        click.echo(
            f"\nMatched {result.kept_count} / {result.kept_count + result.removed_count} keys.",
            err=True,
        )
