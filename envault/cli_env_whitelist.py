"""CLI commands for env-whitelist feature."""
from __future__ import annotations

from pathlib import Path
from typing import List

import click

from envault.env_whitelist import whitelist_file


@click.group("whitelist")
def whitelist_cmd() -> None:
    """Keep only allowed keys in an env file."""


@whitelist_cmd.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("-k", "--key", "keys", multiple=True, help="Exact key to keep.")
@click.option("-p", "--pattern", "patterns", multiple=True, help="Glob pattern to keep (e.g. DB_*).")
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None, help="Output file (default: overwrite src).")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
def run_cmd(
    src: Path,
    keys: List[str],
    patterns: List[str],
    output: Path | None,
    dry_run: bool,
) -> None:
    """Apply whitelist to SRC, keeping only specified keys / patterns."""
    if not keys and not patterns:
        raise click.UsageError("Provide at least one --key or --pattern.")

    try:
        if dry_run:
            # Redirect output to a temp path so we don't overwrite
            import tempfile, shutil
            with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            shutil.copy(src, tmp_path)
            result = whitelist_file(tmp_path, list(keys), patterns=list(patterns))
            tmp_path.unlink(missing_ok=True)
        else:
            result = whitelist_file(src, list(keys), patterns=list(patterns), output=output)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))

    click.echo(f"Kept {result.kept_count} key(s): {', '.join(result.kept) or '(none)'}")
    click.echo(f"Removed {result.removed_count} key(s): {', '.join(result.removed) or '(none)'}")
    if dry_run:
        click.echo("[dry-run] No files were modified.")
        click.echo(result.output)
