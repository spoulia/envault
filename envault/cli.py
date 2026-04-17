"""CLI entry point for envault."""

import click
from envault.vault import lock, unlock


@click.group()
def cli():
    """envault — encrypt and sync .env files securely."""


@cli.command()
@click.argument("env_file", default=".env")
@click.option("--output", "-o", default=None, help="Output vault file path.")
@click.password_option("--password", "-p", prompt="Encryption password")
def lock_cmd(env_file, output, password):
    """Encrypt an .env file into a .vault file."""
    try:
        out = lock(env_file, password, output)
        click.secho(f"Locked: {out}", fg="green")
    except FileNotFoundError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@cli.command()
@click.argument("vault_file", default=".env.vault")
@click.option("--output", "-o", default=None, help="Output .env file path.")
@click.option("--password", "-p", prompt="Decryption password", hide_input=True)
def unlock_cmd(vault_file, output, password):
    """Decrypt a .vault file into an .env file."""
    try:
        out = unlock(vault_file, password, output)
        click.secho(f"Unlocked: {out}", fg="green")
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


cli.add_command(lock_cmd, name="lock")
cli.add_command(unlock_cmd, name="unlock")

if __name__ == "__main__":
    cli()
