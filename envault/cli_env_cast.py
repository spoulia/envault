"""CLI commands for env-cast feature."""
import json
from pathlib import Path

import click

from .env_cast import cast_env, SUPPORTED_TYPES


@click.group("cast")
def cast():
    """Cast .env values to typed Python objects."""


@cast.command("run")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("-r", "--rule", "rules", multiple=True,
              metavar="KEY:TYPE",
              help=f"Casting rule, e.g. PORT:int. Supported: {', '.join(SUPPORTED_TYPES)}")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON.")
def run_cmd(env_file: Path, rules: tuple[str, ...], as_json: bool):
    """Cast values in ENV_FILE according to --rule options."""
    rule_map: dict[str, str] = {}
    for r in rules:
        if ":" not in r:
            raise click.BadParameter(f"Rule must be KEY:TYPE, got {r!r}")
        key, _, type_name = r.partition(":")
        rule_map[key.strip()] = type_name.strip()

    result = cast_env(env_file, rule_map)

    if result.errors:
        for err in result.errors:
            click.echo(click.style(f"  error  {err}", fg="red"))

    if as_json:
        click.echo(json.dumps(result.casted, indent=2, default=str))
        return

    for key, value in result.casted.items():
        type_label = type(value).__name__
        click.echo(f"  {key} = {value!r}  ({type_label})")

    if result.skipped:
        click.echo(f"\n{len(result.skipped)} key(s) not in rules — kept as str.")
