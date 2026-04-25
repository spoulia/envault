"""CLI commands for env type-checking."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envault.env_typecheck import has_issues, typecheck_env


@click.group("typecheck")
def typecheck_cmd() -> None:
    """Check .env value types against a type map."""


@typecheck_cmd.command("check")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--types",
    "types_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="JSON file mapping KEY -> type (str|int|float|bool|url|email|json).",
)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on any issue.")
def check_cmd(env_file: Path, types_file: Path, strict: bool) -> None:
    """Validate .env value types using a JSON type-map file."""
    try:
        type_map: dict = json.loads(types_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        click.echo(f"Error reading types file: {exc}", err=True)
        raise SystemExit(1)

    result = typecheck_env(env_file, type_map)

    if not has_issues(result):
        click.echo(
            f"\u2713 All {result.checked} checked key(s) passed type validation."
        )
        return

    click.echo(
        f"Found {len(result.issues)} type issue(s) "
        f"({result.checked} checked, {result.skipped} skipped):"
    )
    for issue in result.issues:
        click.echo(f"  [{issue.expected}] {issue.key}: {issue.message}")

    if strict:
        raise SystemExit(1)


@typecheck_cmd.command("init")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None)
def init_cmd(env_file: Path, output: Path | None) -> None:
    """Scaffold a type-map JSON file from an existing .env (all keys default to 'str')."""
    type_map: dict = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.partition("=")[0].strip()
        type_map[key] = "str"

    payload = json.dumps(type_map, indent=2)
    if output:
        output.write_text(payload)
        click.echo(f"Type-map written to {output}")
    else:
        click.echo(payload)
