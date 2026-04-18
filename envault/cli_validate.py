"""CLI commands for env file validation."""
from __future__ import annotations
import json
from pathlib import Path

import click

from .env_validate import validate_file


@click.group()
def validate():
    """Validate .env files against a schema."""


@validate.command("check")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--required", multiple=True, help="Keys that must be present.")
@click.option("--nonempty", multiple=True, help="Keys that must not be empty.")
@click.option(
    "--pattern",
    "patterns",
    multiple=True,
    metavar="KEY=REGEX",
    help="Key=regex pairs for value validation.",
)
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON.")
def check_cmd(env_file: Path, required, nonempty, patterns, as_json):
    """Check ENV_FILE against the given rules."""
    parsed_patterns: dict[str, str] = {}
    for p in patterns:
        if "=" not in p:
            raise click.BadParameter(f"Pattern must be KEY=REGEX, got: {p}")
        k, _, v = p.partition("=")
        parsed_patterns[k] = v

    try:
        result = validate_file(
            env_file,
            required=list(required),
            nonempty=list(nonempty),
            patterns=parsed_patterns,
        )
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if as_json:
        data = [{"key": i.key, "message": i.message, "severity": i.severity} for i in result.issues]
        click.echo(json.dumps(data, indent=2))
    else:
        if not result.issues:
            click.echo("✓ No issues found.")
        for issue in result.issues:
            icon = "✗" if issue.severity == "error" else "⚠"
            click.echo(f"{icon} [{issue.severity.upper()}] {issue.key}: {issue.message}")

    raise SystemExit(0 if result.ok else 1)
