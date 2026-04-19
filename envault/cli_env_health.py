"""CLI commands for env health checks."""
import click
from pathlib import Path
from envault.env_health import check_health


@click.group("health")
def health_cmd():
    """Check the health of a .env file."""


@health_cmd.command("check")
@click.argument("env_file", default=".env")
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too.")
def check_cmd(env_file: str, strict: bool):
    """Run health checks on ENV_FILE."""
    result = check_health(Path(env_file))

    if not result.issues:
        click.echo(click.style(f"✓ {env_file} looks healthy ({result.total_keys} keys).", fg="green"))
        return

    for issue in result.issues:
        color = {"error": "red", "warning": "yellow", "info": "cyan"}.get(issue.level, "white")
        prefix = issue.level.upper().ljust(7)
        click.echo(click.style(f"[{prefix}] {issue.message}", fg=color))

    errors = len(result.errors)
    warnings = len(result.warnings)
    click.echo(f"\n{errors} error(s), {warnings} warning(s) in {env_file}.")

    if errors > 0 or (strict and warnings > 0):
        raise SystemExit(1)
