"""CLI commands for managing vault operation hooks."""
import click
from envault.hooks import add_hook, remove_hook, get_hooks, VALID_EVENTS


@click.group()
def hooks():
    """Manage pre/post operation hooks."""
    pass


@hooks.command("add")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.argument("command")
def add_cmd(event, command):
    """Register a hook command for an event."""
    try:
        add_hook(event, command)
        click.echo(f"Hook added for '{event}': {command}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks.command("remove")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.argument("command")
def remove_cmd(event, command):
    """Remove a registered hook."""
    try:
        remove_hook(event, command)
        click.echo(f"Hook removed for '{event}': {command}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks.command("list")
@click.argument("event", type=click.Choice(VALID_EVENTS), required=False)
def list_cmd(event):
    """List registered hooks, optionally filtered by event."""
    events = [event] if event else VALID_EVENTS
    found = False
    for ev in events:
        cmds = get_hooks(ev)
        if cmds:
            found = True
            click.echo(f"[{ev}]")
            for cmd in cmds:
                click.echo(f"  {cmd}")
    if not found:
        click.echo("No hooks registered.")
