"""CLI commands for field-level encryption."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_encrypt_field import decrypt_fields, encrypt_fields


@click.group("field-encrypt")
def field_encrypt_cmd() -> None:
    """Encrypt or decrypt individual .env values."""


@field_encrypt_cmd.command("encrypt")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option("--key", "keys", multiple=True, help="Key(s) to encrypt (default: all).")
@click.option("--overwrite", is_flag=True, default=False, help="Re-encrypt already-encrypted values.")
def encrypt_cmd(env_file: Path, password: str, keys: tuple[str, ...], overwrite: bool) -> None:
    """Encrypt values in ENV_FILE."""
    result = encrypt_fields(
        env_file,
        password,
        list(keys) if keys else None,
        overwrite=overwrite,
    )
    if result.processed:
        click.echo(f"Encrypted {len(result.processed)} key(s): {', '.join(result.processed)}")
    if result.skipped:
        click.echo(f"Skipped (already encrypted): {', '.join(result.skipped)}")
    if not result.processed and not result.skipped:
        click.echo("No keys matched.")


@field_encrypt_cmd.command("decrypt")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--password", prompt=True, hide_input=True, help="Encryption password.")
@click.option("--key", "keys", multiple=True, help="Key(s) to decrypt (default: all encrypted).")
def decrypt_cmd(env_file: Path, password: str, keys: tuple[str, ...]) -> None:
    """Decrypt values in ENV_FILE."""
    try:
        result = decrypt_fields(
            env_file,
            password,
            list(keys) if keys else None,
        )
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc
    if result.processed:
        click.echo(f"Decrypted {len(result.processed)} key(s): {', '.join(result.processed)}")
    if result.skipped:
        click.echo(f"Skipped (not encrypted): {', '.join(result.skipped)}")
    if not result.processed and not result.skipped:
        click.echo("No encrypted keys found.")
