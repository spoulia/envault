"""Tests for envault.env_audit_trail."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_audit_trail import (
    record_change,
    get_trail,
    clear_trail,
    TrailEntry,
    TrailResult,
)


@pytest.fixture()
def trail_file(tmp_path: Path) -> Path:
    return tmp_path / "trail.json"


def test_record_creates_trail_entry(trail_file):
    entry = record_change("DB_URL", None, "postgres://", "set", "prod.env", trail_file)
    assert isinstance(entry, TrailEntry)
    assert entry.key == "DB_URL"
    assert entry.action == "set"


def test_record_persists_to_file(trail_file):
    record_change("SECRET", None, "abc", "set", "dev.env", trail_file)
    result = get_trail(trail_file=trail_file)
    assert result.count == 1
    assert result.entries[0].key == "SECRET"


def test_get_trail_empty_when_no_file(trail_file):
    result = get_trail(trail_file=trail_file)
    assert result.count == 0
    assert isinstance(result, TrailResult)


def test_get_trail_filter_by_key(trail_file):
    record_change("A", None, "1", "set", "f.env", trail_file)
    record_change("B", None, "2", "set", "f.env", trail_file)
    result = get_trail(key="A", trail_file=trail_file)
    assert result.count == 1
    assert result.entries[0].key == "A"


def test_get_trail_filter_by_source(trail_file):
    record_change("X", None, "v", "set", "prod.env", trail_file)
    record_change("Y", None, "v", "set", "dev.env", trail_file)
    result = get_trail(source="prod.env", trail_file=trail_file)
    assert result.count == 1
    assert result.entries[0].source == "prod.env"


def test_clear_trail_removes_entries(trail_file):
    record_change("Z", "old", None, "unset", "x.env", trail_file)
    clear_trail(trail_file)
    result = get_trail(trail_file=trail_file)
    assert result.count == 0


def test_invalid_action_raises(trail_file):
    with pytest.raises(ValueError, match="Unknown action"):
        record_change("K", None, "v", "delete", "f.env", trail_file)


def test_multiple_records_accumulate(trail_file):
    for i in range(5):
        record_change(f"KEY{i}", None, str(i), "import", "bulk.env", trail_file)
    result = get_trail(trail_file=trail_file)
    assert result.count == 5


def test_rename_action_stored(trail_file):
    entry = record_change("OLD_KEY", None, "NEW_KEY", "rename", "env.env", trail_file)
    assert entry.action == "rename"
    result = get_trail(key="OLD_KEY", trail_file=trail_file)
    assert result.entries[0].new_value == "NEW_KEY"
