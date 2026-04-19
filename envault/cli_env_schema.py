"""CLI commands for schema validation."""
import json
from pathlib import Path

import click

from envault.env_schema import validate_schema


@click.group("schema")
def schema():
    """Validate .env files against a JSON schema."""


@schema.command("check")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("schema_file", type=click.Path(exists=True, path_type=Path))
@click.option("--json-output", is_flag=True, help="Output results as JSON")
def check_cmd(env_file: Path, schema_file: Path, json_output: bool):
    """Check ENV_FILE against SCHEMA_FILE."""
    try:
        result = validate_schema(env_file, schema_file)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if json_output:
        data = [{"key": i.key, "message": i.message, "severity": i.severity} for i in result.issues]
        click.echo(json.dumps(data, indent=2))
    else:
        if not result.issues:
            click.echo("Schema validation passed — no issues found.")
        else:
            for issue in result.issues:
                tag = "ERROR" if issue.severity == "error" else "WARN"
                click.echo(f"[{tag}] {issue.key}: {issue.message}")

    if not result.valid:
        raise SystemExit(1)


@schema.command("init")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output", type=click.Path(path_type=Path))
def init_cmd(env_file: Path, output: Path):
    """Generate a starter schema from an existing ENV_FILE."""
    keys: dict = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, _ = line.partition("=")
        keys[k.strip()] = {"required": True, "type": "string"}
    schema = {"keys": keys}
    output.write_text(json.dumps(schema, indent=2))
    click.echo(f"Schema written to {output}")
