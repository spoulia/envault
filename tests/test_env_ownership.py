"""Tests for envault/env_ownership.py"""
import pytest
from pathlib import Path

from envault.env_ownership import (
    assign_owner,
    update_owner,
    remove_owner,
    get_ownership,
    OwnershipEntry,
    OwnershipResult,
)


@pytest.fixture()
def reg(tmp_path) -> Path:
    return tmp_path / "ownership.json"


def test_assign_owner_creates_entry(reg):
    entry = assign_owner("DB_PASSWORD", "alice", registry=reg)
    assert isinstance(entry, OwnershipEntry)
    assert entry.key == "DB_PASSWORD"
    assert entry.owner == "alice"


def test_assign_owner_persists(reg):
    assign_owner("API_KEY", "bob", registry=reg)
    result = get_ownership(registry=reg)
    keys = [e.key for e in result.entries]
    assert "API_KEY" in keys


def test_assign_duplicate_raises(reg):
    assign_owner("SECRET", "alice", registry=reg)
    with pytest.raises(ValueError, match="already assigned"):
        assign_owner("SECRET", "bob", registry=reg)


def test_assign_with_team_and_notes(reg):
    entry = assign_owner("JWT_SECRET", "carol", team="backend", notes="rotate monthly", registry=reg)
    assert entry.team == "backend"
    assert entry.notes == "rotate monthly"


def test_update_owner_changes_owner(reg):
    assign_owner("DB_URL", "alice", registry=reg)
    entry = update_owner("DB_URL", "dave", registry=reg)
    assert entry.owner == "dave"


def test_update_owner_creates_if_missing(reg):
    entry = update_owner("NEW_KEY", "eve", registry=reg)
    assert entry.owner == "eve"


def test_remove_owner_deletes_entry(reg):
    assign_owner("OLD_KEY", "alice", registry=reg)
    removed = remove_owner("OLD_KEY", registry=reg)
    assert removed is True
    result = get_ownership(registry=reg)
    assert all(e.key != "OLD_KEY" for e in result.entries)


def test_remove_missing_key_returns_false(reg):
    assert remove_owner("GHOST_KEY", registry=reg) is False


def test_get_ownership_empty_when_no_file(reg):
    result = get_ownership(registry=reg)
    assert isinstance(result, OwnershipResult)
    assert result.count == 0


def test_by_owner_filters_correctly(reg):
    assign_owner("KEY_A", "alice", registry=reg)
    assign_owner("KEY_B", "bob", registry=reg)
    result = get_ownership(registry=reg)
    alice_entries = result.by_owner("alice")
    assert len(alice_entries) == 1
    assert alice_entries[0].key == "KEY_A"


def test_by_team_filters_correctly(reg):
    assign_owner("KEY_X", "alice", team="frontend", registry=reg)
    assign_owner("KEY_Y", "bob", team="backend", registry=reg)
    result = get_ownership(registry=reg)
    fe = result.by_team("frontend")
    assert len(fe) == 1
    assert fe[0].key == "KEY_X"
