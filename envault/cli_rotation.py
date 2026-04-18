"""CLI commands for key rotation."""

from __future__ import annotations

from pathlib import Path

import click

from envault.rotation import rotate, rotate_and_backup


@click.group()
def rotation() -> None:
    """Key rotation commands."""


@rotation.command("rotate")
@click.option("--vault", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--old-password", prompt=True, hide_input=True, help="Current vault password.")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True, help="New vault password.")
@click.option("--backup", is_flag=True, default=False, help="Keep a .bak copy of the old vault.")
def rotate_cmd(vault: str, old_password: str, new_password: str, backup: bool) -> None:
    """Re-encrypt the vault with a new password."""
    vault_path = Path(vault)
    try:
        if backup:
            bak = rotate_and_backup(vault_path, old_password, new_password)
            click.echo(f"Backup saved to {bak}")
        else:
            rotate(vault_path, old_password, new_password)
        click.echo("Key rotation successful.")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError:
        click.echo("Error: incorrect old password.", err=True)
        raise SystemExit(1)
