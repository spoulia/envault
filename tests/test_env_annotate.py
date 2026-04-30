"""Tests for envault/env_annotate.py."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_annotate import (
    AnnotationEntry,
    AnnotationResult,
    add_annotation,
    get_annotations,
    remove_annotation,
    update_annotation,
)


@pytest.fixture()
def ann_file(tmp_path: Path) -> Path:
    return tmp_path / "annotations.json"


def test_add_annotation_creates_entry(ann_file):
    entry = add_annotation("DB_HOST", "Primary database host", path=ann_file)
    assert isinstance(entry, AnnotationEntry)
    assert entry.key == "DB_HOST"
    assert entry.note == "Primary database host"


def test_add_annotation_persists(ann_file):
    add_annotation("DB_HOST", "Primary database host", path=ann_file)
    result = get_annotations(path=ann_file)
    assert result.count == 1
    assert result.entries[0].key == "DB_HOST"


def test_add_duplicate_annotation_raises(ann_file):
    add_annotation("DB_HOST", "First note", path=ann_file)
    with pytest.raises(ValueError, match="already exists"):
        add_annotation("DB_HOST", "Second note", path=ann_file)


def test_add_annotation_with_author_and_tags(ann_file):
    entry = add_annotation(
        "SECRET_KEY", "Django secret key", author="alice", tags=["security", "django"], path=ann_file
    )
    assert entry.author == "alice"
    assert "security" in entry.tags


def test_get_annotations_empty_when_no_file(ann_file):
    result = get_annotations(path=ann_file)
    assert isinstance(result, AnnotationResult)
    assert result.count == 0


def test_get_annotations_for_key(ann_file):
    add_annotation("DB_HOST", "Host note", path=ann_file)
    add_annotation("DB_PORT", "Port note", path=ann_file)
    result = get_annotations(path=ann_file)
    entry = result.for_key("DB_PORT")
    assert entry is not None
    assert entry.note == "Port note"


def test_update_annotation_changes_note(ann_file):
    add_annotation("DB_HOST", "Old note", path=ann_file)
    updated = update_annotation("DB_HOST", "New note", path=ann_file)
    assert updated.note == "New note"
    result = get_annotations(path=ann_file)
    assert result.for_key("DB_HOST").note == "New note"


def test_update_missing_annotation_raises(ann_file):
    with pytest.raises(KeyError):
        update_annotation("MISSING", "Some note", path=ann_file)


def test_remove_annotation_deletes_entry(ann_file):
    add_annotation("DB_HOST", "Host note", path=ann_file)
    remove_annotation("DB_HOST", path=ann_file)
    result = get_annotations(path=ann_file)
    assert result.count == 0


def test_remove_missing_annotation_raises(ann_file):
    with pytest.raises(KeyError):
        remove_annotation("MISSING", path=ann_file)
