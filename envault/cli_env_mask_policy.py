"""CLI commands for managing .env masking policies."""
from __future__ import annotations

import click

from envault.env_mask_policy import (
    add_policy,
    enforce_policy,
    list_policies,
    remove_policy,
)
from envault.vault import unlock


@click.group("mask-policy")
def mask_policy_cmd() -> None:
    """Manage key masking / blocking policies."""


@mask_policy_cmd.command("add")
@click.argument("pattern")
@click.option(
    "--action",
    type=click.Choice(["mask", "block", "allow"]),
    default="mask",
    show_default=True,
    help="Action to apply when pattern matches.",
)
@click.option("--description", "-d", default="", help="Human-readable description.")
def add_cmd(pattern: str, action: str, description: str) -> None:
    """Add a new masking policy entry."""
    try:
        entry = add_policy(pattern, action, description)
        click.echo(f"Added policy: '{entry.pattern}' → {entry.action}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@mask_policy_cmd.command("remove")
@click.argument("pattern")
def remove_cmd(pattern: str) -> None:
    """Remove a masking policy entry by pattern."""
    removed = remove_policy(pattern)
    if removed:
        click.echo(f"Removed policy for pattern '{pattern}'.")
    else:
        click.echo(f"No policy found for pattern '{pattern}'.", err=True)
        raise SystemExit(1)


@mask_policy_cmd.command("list")
def list_cmd() -> None:
    """List all masking policies."""
    entries = list_policies()
    if not entries:
        click.echo("No policies defined.")
        return
    for e in entries:
        desc = f"  # {e.description}" if e.description else ""
        click.echo(f"  {e.pattern:<30} {e.action}{desc}")


@mask_policy_cmd.command("enforce")
@click.argument("vault", type=click.Path(exists=True))
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def enforce_cmd(vault: str, password: str) -> None:
    """Enforce policies against a locked vault."""
    try:
        env_text = unlock(vault, password)
    except Exception as exc:
        click.echo(f"Error unlocking vault: {exc}", err=True)
        raise SystemExit(1)

    env = dict(
        line.split("=", 1)
        for line in env_text.splitlines()
        if "=" in line and not line.startswith("#")
    )
    result = enforce_policy(env)
    if result.has_violations:
        click.echo("Policy violations found:")
        for key in result.violations:
            click.echo(f"  BLOCKED: {key}")
        raise SystemExit(1)
    click.echo("All keys comply with masking policies.")
