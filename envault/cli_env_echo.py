"""CLI commands for env-echo: print decrypted vault contents."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_echo import echo_vault, format_echo


@click.group("echo")
def echo_cmd() -> None:
    """Print decrypted vault key/value pairs."""


@echo_cmd.command("show")
@click.argument("vault", type=click.Path(exists=True, path_type=Path))
@click.option("--password", "-p", required=True, help="Vault password.")
@click.option("--key", "-k", multiple=True, help="Only show specific key(s).")
@click.option("--prefix", default=None, help="Filter keys by prefix.")
@click.option("--no-mask", is_flag=True, default=False, help="Disable masking of sensitive values.")
@click.option("--export", "export_fmt", is_flag=True, default=False, help="Prefix lines with 'export '.")
def show_cmd(
    vault: Path,
    password: str,
    key: tuple,
    prefix: str,
    no_mask: bool,
    export_fmt: bool,
) -> None:
    """Decrypt and print vault contents."""
    try:
        result = echo_vault(
            vault,
            password,
            keys=list(key) if key else None,
            mask=not no_mask,
            prefix=prefix,
        )
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    if result.count == 0:
        click.echo("No matching keys found.")
        return

    output = format_echo(result)
    if export_fmt:
        output = "\n".join(f"export {line}" for line in output.splitlines())
    click.echo(output)

    if result.masked_keys:
        click.echo(
            f"\n# {len(result.masked_keys)} sensitive key(s) masked: {', '.join(result.masked_keys)}",
            err=True,
        )
