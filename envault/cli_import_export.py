"""CLI commands for bulk import/export of .env variables."""
import click
from pathlib import Path
from .import_export import export_env, import_env


@click.group()
def impexp():
    """Bulk import/export .env variables."""


@impexp.command("export")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "fmt", type=click.Choice(["csv", "json"]), default="json", show_default=True)
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None,
              help="Output file (default: print to stdout)")
def export_cmd(env_file: Path, fmt: str, output: Path | None):
    """Export an .env file to JSON or CSV."""
    try:
        result = export_env(env_file, fmt)  # type: ignore[arg-type]
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if output:
        output.write_text(result)
        click.echo(f"Exported to {output}")
    else:
        click.echo(result)


@impexp.command("import")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("env_file", type=click.Path(path_type=Path))
@click.option("--format", "fmt", type=click.Choice(["csv", "json"]), default="json", show_default=True)
@click.option("--merge", is_flag=True, default=False, help="Merge with existing keys instead of replacing.")
def import_cmd(input_file: Path, env_file: Path, fmt: str, merge: bool):
    """Import JSON or CSV into an .env file."""
    content = input_file.read_text()
    try:
        count = import_env(env_file, content, fmt, merge=merge)  # type: ignore[arg-type]
    except (ValueError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    action = "Merged" if merge else "Imported"
    click.echo(f"{action} {count} key(s) into {env_file}")
