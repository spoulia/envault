"""CLI commands for vault tagging."""
import click
from envault.tags import add_tag, remove_tag, get_tags, list_tagged, clear_tags


@click.group()
def tags():
    """Manage tags for vault files."""
    pass


@tags.command("add")
@click.argument("vault")
@click.argument("tag")
def add_cmd(vault, tag):
    """Add a tag to a vault."""
    try:
        add_tag(vault, tag)
        click.echo(f"Tag '{tag}' added to '{vault}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@tags.command("remove")
@click.argument("vault")
@click.argument("tag")
def remove_cmd(vault, tag):
    """Remove a tag from a vault."""
    try:
        remove_tag(vault, tag)
        click.echo(f"Tag '{tag}' removed from '{vault}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)


@tags.command("list")
@click.argument("vault")
def list_cmd(vault):
    """List all tags for a vault."""
    tag_list = get_tags(vault)
    if not tag_list:
        click.echo("No tags found.")
    else:
        for t in tag_list:
            click.echo(t)


@tags.command("find")
@click.argument("tag")
def find_cmd(tag):
    """Find all vaults with a given tag."""
    vaults = list_tagged(tag)
    if not vaults:
        click.echo(f"No vaults tagged '{tag}'.")
    else:
        for v in vaults:
            click.echo(v)


@tags.command("clear")
@click.argument("vault")
def clear_cmd(vault):
    """Clear all tags from a vault."""
    clear_tags(vault)
    click.echo(f"All tags cleared from '{vault}'.")
