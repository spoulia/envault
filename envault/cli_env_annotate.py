"""CLI commands for env-annotate feature."""
from __future__ import annotations

from pathlib import Path

import click

from .env_annotate import add_annotation, get_annotations, remove_annotation, update_annotation


@click.group("annotate")
def annotate_cmd() -> None:
    """Manage inline annotations for .env keys."""


@annotate_cmd.command("add")
@click.argument("key")
@click.argument("note")
@click.option("--author", default=None, help="Author of the annotation.")
@click.option("--tag", "tags", multiple=True, help="Tags for the annotation.")
@click.option("--file", "ann_file", default=".envault_annotations.json", show_default=True)
def add_cmd(key: str, note: str, author: str, tags: tuple, ann_file: str) -> None:
    """Add an annotation for KEY."""
    try:
        entry = add_annotation(key, note, author=author, tags=list(tags), path=Path(ann_file))
        click.echo(f"✔ Annotation added for '{entry.key}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@annotate_cmd.command("update")
@click.argument("key")
@click.argument("note")
@click.option("--author", default=None)
@click.option("--tag", "tags", multiple=True)
@click.option("--file", "ann_file", default=".envault_annotations.json", show_default=True)
def update_cmd(key: str, note: str, author: str, tags: tuple, ann_file: str) -> None:
    """Update an existing annotation for KEY."""
    try:
        entry = update_annotation(key, note, author=author, tags=list(tags), path=Path(ann_file))
        click.echo(f"✔ Annotation updated for '{entry.key}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@annotate_cmd.command("remove")
@click.argument("key")
@click.option("--file", "ann_file", default=".envault_annotations.json", show_default=True)
def remove_cmd(key: str, ann_file: str) -> None:
    """Remove the annotation for KEY."""
    try:
        remove_annotation(key, path=Path(ann_file))
        click.echo(f"✔ Annotation removed for '{key}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@annotate_cmd.command("list")
@click.option("--file", "ann_file", default=".envault_annotations.json", show_default=True)
def list_cmd(ann_file: str) -> None:
    """List all annotations."""
    result = get_annotations(path=Path(ann_file))
    if not result.entries:
        click.echo("No annotations found.")
        return
    for e in result.entries:
        author_part = f"  [{e.author}]" if e.author else ""
        tags_part = f"  tags={e.tags}" if e.tags else ""
        click.echo(f"{e.key}: {e.note}{author_part}{tags_part}")
