"""CLI commands for sharing encrypted vault bundles."""

import click
from pathlib import Path
from envault.sharing import export_bundle, import_bundle


@click.group()
def share():
    """Commands for sharing vault bundles with team members."""


@share.command("export")
@click.argument("vault_file", default=".env.vault")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--recipient", default="", help="Optional recipient hint (e.g. email).")
@click.option(
    "--output",
    "-o",
    default="vault_bundle.json",
    show_default=True,
    help="Output bundle file path.",
)
def export_cmd(vault_file: str, password: str, recipient: str, output: str) -> None:
    """Export an encrypted vault bundle suitable for sharing."""
    try:
        bundle_json = export_bundle(vault_file, password, recipient)
        Path(output).write_text(bundle_json)
        click.echo(f"Bundle exported to {output}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Export failed: {exc}")


@share.command("import")
@click.argument("bundle_file", default="vault_bundle.json")
@click.option("--password", prompt=True, hide_input=True, help="Bundle password.")
@click.option(
    "--output",
    "-o",
    default=".env.vault",
    show_default=True,
    help="Destination vault file path.",
)
def import_cmd(bundle_file: str, password: str, output: str) -> None:
    """Import a shared vault bundle and write the vault file locally."""
    try:
        bundle_json = Path(bundle_file).read_text()
        import_bundle(bundle_json, password, output)
        click.echo(f"Vault imported to {output}")
    except FileNotFoundError:
        raise click.ClickException(f"Bundle file not found: {bundle_file}")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Import failed: {exc}")
