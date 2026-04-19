"""CLI commands for env key pinning."""
import click
from pathlib import Path
from envault.env_pin import pin_key, unpin_key, list_pins, check_violations, DEFAULT_PIN_FILE


@click.group()
def pin():
    """Pin env keys to fixed values."""


@pin.command("add")
@click.argument("key")
@click.argument("value")
@click.option("--pin-file", default=str(DEFAULT_PIN_FILE), show_default=True)
def add_cmd(key, value, pin_file):
    """Pin KEY to VALUE."""
    pin_key(key, value, Path(pin_file))
    click.echo(f"Pinned {key}={value}")


@pin.command("remove")
@click.argument("key")
@click.option("--pin-file", default=str(DEFAULT_PIN_FILE), show_default=True)
def remove_cmd(key, pin_file):
    """Remove pin for KEY."""
    removed = unpin_key(key, Path(pin_file))
    if removed:
        click.echo(f"Unpinned {key}")
    else:
        click.echo(f"Key '{key}' was not pinned.")


@pin.command("list")
@click.option("--pin-file", default=str(DEFAULT_PIN_FILE), show_default=True)
def list_cmd(pin_file):
    """List all pinned keys."""
    pins = list_pins(Path(pin_file))
    if not pins:
        click.echo("No pinned keys.")
        return
    for k, v in pins.items():
        click.echo(f"{k}={v}")


@pin.command("check")
@click.argument("env_file")
@click.option("--pin-file", default=str(DEFAULT_PIN_FILE), show_default=True)
def check_cmd(env_file, pin_file):
    """Check ENV_FILE for pin violations."""
    result = check_violations(Path(env_file), Path(pin_file))
    if result.violations:
        click.echo("Pin violations detected:")
        for k in result.violations:
            click.echo(f"  [VIOLATION] {k}")
        raise SystemExit(1)
    else:
        click.echo(f"All pins OK. ({len(result.pinned)} checked, {len(result.skipped)} skipped)")
