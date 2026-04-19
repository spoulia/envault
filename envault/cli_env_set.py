"""CLI commands: set / unset / list keys in a vault."""
import click
from pathlib import Path
from envault.env_set import set_keys, unset_keys, list_keys


@click.group()
def envset():
    """Manage individual keys inside a vault."""


@envset.command("set")
@click.argument("vault")
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--no-overwrite", is_flag=True, default=False)
def set_cmd(vault, pairs, password, no_overwrite):
    """Set KEY=VALUE pairs in VAULT."""
    updates = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair}")
        k, _, v = pair.partition("=")
        updates[k.strip()] = v.strip()
    result = set_keys(Path(vault), password, updates, overwrite=not no_overwrite)
    for k in result.set:
        click.echo(f"set: {k}")
    for k in result.skipped:
        click.echo(f"skipped (exists): {k}")


@envset.command("unset")
@click.argument("vault")
@click.argument("keys", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True)
def unset_cmd(vault, keys, password):
    """Remove KEYS from VAULT."""
    result = unset_keys(Path(vault), password, list(keys))
    for k in result.unset:
        click.echo(f"unset: {k}")
    for k in result.skipped:
        click.echo(f"not found: {k}")


@envset.command("list")
@click.argument("vault")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--show-values", is_flag=True, default=False)
def list_cmd(vault, password, show_values):
    """List all keys (and optionally values) in VAULT."""
    pairs = list_keys(Path(vault), password)
    if not pairs:
        click.echo("(empty)")
        return
    for k, v in pairs.items():
        if show_values:
            click.echo(f"{k}={v}")
        else:
            click.echo(k)
