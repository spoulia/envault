"""CLI commands for signing and verifying .env files."""
import sys
from pathlib import Path

import click

from envault.env_sign import sign_file, verify_file


@click.group("sign")
def sign_cmd() -> None:
    """Sign and verify .env files with an HMAC secret."""


@sign_cmd.command("sign")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--secret", required=True, envvar="ENVAULT_SIGN_SECRET", help="HMAC secret key.")
@click.option("--output", default=None, help="Path for the signature file (default: <env_file>.sig).")
def do_sign(env_file: str, secret: str, output: str | None) -> None:
    """Sign ENV_FILE and write a .sig file."""
    result = sign_file(env_file, secret, sig_path=output)
    sig_path = output or str(Path(env_file).with_suffix(".sig"))
    click.echo(f"Signed: {result.file}")
    click.echo(f"Signature written to: {sig_path}")
    click.echo(f"Digest ({result.algorithm}): {result.signature}")


@sign_cmd.command("verify")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--secret", required=True, envvar="ENVAULT_SIGN_SECRET", help="HMAC secret key.")
@click.option("--sig", default=None, help="Path to the signature file (default: <env_file>.sig).")
def do_verify(env_file: str, secret: str, sig: str | None) -> None:
    """Verify the signature of ENV_FILE."""
    result = verify_file(env_file, secret, sig_path=sig)
    if result.valid:
        click.echo(f"✔  Signature valid: {result.file}")
    else:
        click.echo(f"✘  Signature invalid: {result.file} — {result.reason}", err=True)
        sys.exit(1)
