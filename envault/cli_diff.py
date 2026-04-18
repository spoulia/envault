"""CLI commands for diffing two vault files."""
import click
from envault.diff import diff_vaults, format_diff


@click.group()
def diff():
    """Compare two encrypted vault files."""


@diff.command("show")
@click.argument("vault_a", type=click.Path(exists=True))
@click.argument("vault_b", type=click.Path(exists=True))
@click.option("--password-a", prompt="Password for vault A", hide_input=True, help="Password for the first vault.")
@click.option("--password-b", prompt="Password for vault B", hide_input=True, help="Password for the second vault.")
@click.option("--summary", is_flag=True, default=False, help="Show counts only.")
def show_cmd(vault_a: str, vault_b: str, password_a: str, password_b: str, summary: bool):
    """Show differences between VAULT_A and VAULT_B."""
    try:
        result = diff_vaults(vault_a, password_a, vault_b, password_b)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if summary:
        click.echo(f"Added:   {len(result.added)}")
        click.echo(f"Removed: {len(result.removed)}")
        click.echo(f"Changed: {len(result.changed)}")
    else:
        click.echo(format_diff(result))
