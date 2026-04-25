"""CLI commands for envault env-lint-fix."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_lint_fix import lint_fix


@click.group("lint-fix")
def lint_fix_cmd() -> None:
    """Auto-fix common .env formatting issues."""


@lint_fix_cmd.command("run")
@click.argument("env_file", default=".env", type=click.Path())
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be fixed without writing changes.",
)
def run_cmd(env_file: str, dry_run: bool) -> None:
    """Apply auto-fixes to ENV_FILE (default: .env)."""
    path = Path(env_file)

    if not path.exists():
        click.echo(f"Error: file not found: {env_file}", err=True)
        raise SystemExit(1)

    if dry_run:
        # Run lint_fix on a temporary copy to preview changes
        import tempfile, shutil

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".env", mode="w"
        ) as tmp:
            tmp_path = Path(tmp.name)
        shutil.copy2(path, tmp_path)
        try:
            result = lint_fix(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
    else:
        result = lint_fix(path)

    if not result.fixes:
        click.echo(f"{env_file}: no issues to fix.")
        return

    mode_label = "[dry-run] would fix" if dry_run else "fixed"
    click.echo(f"{env_file}: {mode_label} {result.fix_count} issue(s):")
    for lineno, description in result.fixes:
        click.echo(f"  line {lineno}: {description}")
