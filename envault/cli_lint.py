"""CLI commands for linting .env files."""
import click
from pathlib import Path
from envault.lint import lint_file


@click.group()
def lint():
    """Lint .env files for common issues."""


@lint.command("check")
@click.argument("env_file", default=".env")
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too.")
def check_cmd(env_file: str, strict: bool):
    """Check ENV_FILE for lint issues."""
    path = Path(env_file)
    try:
        result = lint_file(path)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not result.issues:
        click.echo(f"✓ {path}: no issues found")
        return

    errors = 0
    warnings = 0
    for issue in result.issues:
        tag = issue.severity.upper()
        key_info = f" [{issue.key}]" if issue.key else ""
        click.echo(f"{path}:{issue.line}: {tag}{key_info}: {issue.message}")
        if issue.severity == "error":
            errors += 1
        else:
            warnings += 1

    summary = f"{errors} error(s), {warnings} warning(s)"
    click.echo(f"\n{path}: {summary}")

    if errors or (strict and warnings):
        raise SystemExit(1)
