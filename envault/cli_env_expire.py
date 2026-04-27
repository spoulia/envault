"""CLI commands for managing .env key expiry dates."""
from __future__ import annotations

from pathlib import Path

import click

from .env_expire import (
    DEFAULT_REGISTRY,
    add_expiry,
    check_expiry,
    list_expiries,
    remove_expiry,
)


@click.group("expire")
def expire_cmd() -> None:
    """Manage expiry dates for .env keys."""


@expire_cmd.command("add")
@click.argument("key")
@click.argument("expires_on")
@click.option("--description", "-d", default="", help="Optional note.")
@click.option("--registry", default=str(DEFAULT_REGISTRY), show_default=True)
def add_cmd(key: str, expires_on: str, description: str, registry: str) -> None:
    """Register an expiry date (YYYY-MM-DD) for KEY."""
    try:
        entry = add_expiry(key, expires_on, description, Path(registry))
        click.echo(f"Registered expiry for '{entry.key}' on {entry.expires_on}.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@expire_cmd.command("remove")
@click.argument("key")
@click.option("--registry", default=str(DEFAULT_REGISTRY), show_default=True)
def remove_cmd(key: str, registry: str) -> None:
    """Remove the expiry record for KEY."""
    removed = remove_expiry(key, Path(registry))
    if removed:
        click.echo(f"Removed expiry for '{key}'.")
    else:
        click.echo(f"No expiry record found for '{key}'.")


@expire_cmd.command("list")
@click.option("--registry", default=str(DEFAULT_REGISTRY), show_default=True)
def list_cmd(registry: str) -> None:
    """List all registered expiry dates."""
    result = list_expiries(Path(registry))
    if not result.entries:
        click.echo("No expiry records found.")
        return
    for entry in result.entries:
        desc = f"  # {entry.description}" if entry.description else ""
        click.echo(f"{entry.key}: {entry.expires_on}{desc}")


@expire_cmd.command("check")
@click.option("--warn-days", default=30, show_default=True, help="Days ahead to warn.")
@click.option("--registry", default=str(DEFAULT_REGISTRY), show_default=True)
def check_cmd(warn_days: int, registry: str) -> None:
    """Report expired or soon-to-expire keys."""
    result = check_expiry(warn_days, Path(registry))
    if not result.expired and not result.upcoming:
        click.echo("All keys are within their expiry window.")
        return
    for entry in result.expired:
        click.echo(f"[EXPIRED]  {entry.key} (expired {entry.expires_on})")
    for entry in result.upcoming:
        click.echo(f"[EXPIRING] {entry.key} (expires {entry.expires_on})")
    if result.has_expired:
        raise SystemExit(1)
