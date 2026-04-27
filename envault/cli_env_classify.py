"""CLI commands for env-classify — categorise keys in a .env file."""
import click
from pathlib import Path

from envault.env_classify import classify_file, format_classify


@click.group("classify")
def classify_cmd() -> None:
    """Classify .env keys by category."""


@classify_cmd.command("show")
@click.argument("env_file", default=".env")
@click.option("--category", "-c", default=None, help="Show only keys in this category.")
@click.option("--unclassified", "-u", is_flag=True, help="Show only unclassified keys.")
@click.option("--summary", "-s", is_flag=True, help="Print category counts only.")
def show_cmd(env_file: str, category: str | None, unclassified: bool, summary: bool) -> None:
    """Show classified keys from ENV_FILE."""
    path = Path(env_file)
    try:
        result = classify_file(path)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if summary:
        for cat, keys in sorted(result.categories.items()):
            click.echo(f"{cat}: {len(keys)}")
        click.echo(f"unclassified: {result.unclassified_count}")
        click.echo(f"total: {result.total_keys}")
        return

    if unclassified:
        if not result.unclassified:
            click.echo("No unclassified keys.")
        else:
            for k in sorted(result.unclassified):
                click.echo(k)
        return

    if category:
        keys = result.categories.get(category, [])
        if not keys:
            click.echo(f"No keys found in category '{category}'.")
        else:
            for k in sorted(keys):
                click.echo(k)
        return

    output = format_classify(result)
    if output:
        click.echo(output)
    else:
        click.echo("No keys found.")
