"""CLI commands for masking sensitive .env values."""
import click
from pathlib import Path
from envault.env_mask import mask_env


@click.group("mask")
def mask():
    """Mask sensitive values for safe display."""


@mask.command("show")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--extra", "-e", multiple=True, help="Additional keys to mask.")
@click.option(
    "--reveal", "-r", default=0, show_default=True,
    help="Number of leading characters to reveal.",
)
def show_cmd(env_file: Path, extra: tuple, reveal: int):
    """Display .env file with sensitive values masked."""
    try:
        result = mask_env(env_file, extra_keys=list(extra), reveal_chars=reveal)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for k, v in result.masked.items():
        click.echo(f"{k}={v}")

    click.echo(
        f"\n{len(result.masked_keys)} of {result.total} keys masked.",
        err=True,
    )
