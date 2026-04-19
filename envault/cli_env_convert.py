"""CLI commands for env format conversion."""
import click
from pathlib import Path
from envault.env_convert import convert_env


@click.group("convert")
def convert_cmd():
    """Convert .env files to other formats."""


@convert_cmd.command("run")
@click.argument("src", type=click.Path(exists=True))
@click.argument("dest")
@click.option(
    "--format", "fmt",
    type=click.Choice(["dotenv", "json", "yaml", "toml"]),
    required=True,
    help="Target output format.",
)
def run_cmd(src: str, dest: str, fmt: str):
    """Convert SRC .env file to DEST in the given FORMAT."""
    try:
        result = convert_env(src, dest, fmt)  # type: ignore[arg-type]
        click.echo(
            f"Converted {result.keys_converted} key(s) from {src} "
            f"to {fmt} → {dest}"
        )
        for w in result.warnings:
            click.echo(f"  warning: {w}")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
