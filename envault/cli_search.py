"""CLI commands for vault search."""
import click
from pathlib import Path
from envault.search import search_vault, search_many


@click.group()
def search():
    """Search keys and values inside vaults."""


@search.command("run")
@click.argument("pattern")
@click.option("--vault", "-v", "vaults", multiple=True, default=[".env.vault"], show_default=True)
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.option("--values", is_flag=True, default=False, help="Also search in values.")
@click.option("--ignore-case", "-i", is_flag=True, default=False)
def run_cmd(pattern, vaults, password, values, ignore_case):
    """Search for PATTERN in vault keys (and optionally values)."""
    vault_paths = [Path(v) for v in vaults]
    results = search_many(vault_paths, password, pattern, search_values=values, ignore_case=ignore_case)
    if not results:
        click.echo("No matches found.")
        return
    current_vault = None
    for r in results:
        if r.vault != current_vault:
            click.echo(f"\n[{r.vault}]")
            current_vault = r.vault
        masked = r.value if values else "***"
        click.echo(f"  line {r.line:>4}: {r.key} = {masked}")
    click.echo()
