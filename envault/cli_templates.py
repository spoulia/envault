"""CLI commands for template management."""
import click
from envault.templates import (
    save_template, remove_template, get_template,
    list_templates, check_env_against_template, DEFAULT_TEMPLATES_FILE
)
from pathlib import Path


@click.group()
def templates():
    """Manage .env key templates."""


@templates.command("add")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--description", "-d", default="", help="Optional description.")
def add_cmd(name, keys, description):
    """Add a new template with expected keys."""
    try:
        save_template(name, list(keys), description)
        click.echo(f"Template '{name}' saved with {len(keys)} key(s).")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@templates.command("remove")
@click.argument("name")
def remove_cmd(name):
    """Remove a template."""
    try:
        remove_template(name)
        click.echo(f"Template '{name}' removed.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)


@templates.command("show")
@click.argument("name")
def show_cmd(name):
    """Show keys defined in a template."""
    try:
        tmpl = get_template(name)
        click.echo(f"Template: {name}")
        if tmpl["description"]:
            click.echo(f"Description: {tmpl['description']}")
        click.echo("Keys:")
        for k in tmpl["keys"]:
            click.echo(f"  - {k}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)


@templates.command("list")
def list_cmd():
    """List all saved templates."""
    names = list_templates()
    if not names:
        click.echo("No templates found.")
    for name in names:
        click.echo(name)


@templates.command("check")
@click.argument("name")
@click.argument("env_file", type=click.Path(exists=True))
def check_cmd(name, env_file):
    """Check an .env file against a template."""
    content = Path(env_file).read_text()
    try:
        result = check_env_against_template(content, name)
        if result["missing"]:
            click.echo("Missing keys: " + ", ".join(result["missing"]))
        if result["extra"]:
            click.echo("Extra keys:   " + ", ".join(result["extra"]))
        if not result["missing"] and not result["extra"]:
            click.echo("All keys match the template.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
