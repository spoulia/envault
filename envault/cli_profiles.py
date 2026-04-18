import click
from envault.profiles import add_profile, remove_profile, get_profile, list_profiles


@click.group("profiles")
def profiles():
    """Manage named vault profiles."""
    pass


@profiles.command("add")
@click.argument("name")
@click.argument("vault_path")
@click.option("--description", "-d", default="", help="Optional profile description.")
def add_cmd(name, vault_path, description):
    """Add a new profile NAME pointing to VAULT_PATH."""
    try:
        add_profile(name, vault_path, description=description)
        click.echo(f"Profile '{name}' added -> {vault_path}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles.command("remove")
@click.argument("name")
def remove_cmd(name):
    """Remove profile NAME."""
    try:
        remove_profile(name)
        click.echo(f"Profile '{name}' removed.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles.command("show")
@click.argument("name")
def show_cmd(name):
    """Show details for profile NAME."""
    try:
        profile = get_profile(name)
        click.echo(f"Name       : {name}")
        click.echo(f"Vault Path : {profile['vault_path']}")
        click.echo(f"Description: {profile.get('description', '')}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles.command("list")
def list_cmd():
    """List all profiles."""
    all_profiles = list_profiles()
    if not all_profiles:
        click.echo("No profiles configured.")
        return
    for name, data in all_profiles.items():
        desc = f" — {data['description']}" if data.get("description") else ""
        click.echo(f"  {name}: {data['vault_path']}{desc}")
