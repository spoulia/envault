"""CLI commands for comparing two vault files."""
import click
from pathlib import Path
from envault.compare import compare_vaults, format_compare


@click.group()
def compare():
    """Compare two encrypted vault files."""


@compare.command("show")
@click.argument("vault_a", type=click.Path(exists=True, path_type=Path))
@click.argument("vault_b", type=click.Path(exists=True, path_type=Path))
@click.option("--password-a", prompt="Password for vault A", hide_input=True)
@click.option("--password-b", default=None, help="Password for vault B (defaults to password A)")
@click.option("--label-a", default=None, help="Label for vault A (defaults to filename)")
@click.option("--label-b", default=None, help="Label for vault B (defaults to filename)")
def show_cmd(
    vault_a: Path,
    vault_b: Path,
    password_a: str,
    password_b: str,
    label_a: str,
    label_b: str,
):
    """Show differences between two vaults."""
    if password_b is None:
        password_b = click.prompt("Password for vault B (leave blank to reuse A's password)",
                                  default="", hide_input=True, show_default=False)
        if not password_b:
            password_b = password_a

    la = label_a or vault_a.name
    lb = label_b or vault_b.name

    try:
        result = compare_vaults(vault_a, password_a, vault_b, password_b)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Comparing {la}  vs  {lb}")
    click.echo(format_compare(result, label_a=la, label_b=lb))
    if result.is_identical:
        raise SystemExit(0)
    raise SystemExit(1)
