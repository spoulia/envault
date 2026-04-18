"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path
from envault.audit import record, get_log, clear_log


@pytest.fixture
def log_file(tmp_path):
    return str(tmp_path / "test_audit.json")


def test_record_creates_entry(log_file):
    entry = record("lock", {"file": ".env"}, log_path=log_file)
    assert entry["action"] == "lock"
    assert entry["details"] == {"file": ".env"}
    assert "timestamp" in entry
    assert "user" in entry


def test_record_persists_to_file(log_file):
    record("lock", log_path=log_file)
    record("unlock", log_path=log_file)
    entries = get_log(log_path=log_file)
    assert len(entries) == 2
    assert entries[0]["action"] == "lock"
    assert entries[1]["action"] == "unlock"


def test_get_log_empty_when_no_file(log_file):
    entries = get_log(log_path=log_file)
    assert entries == []


def test_clear_log_removes_entries(log_file):
    record("lock", log_path=log_file)
    record("unlock", log_path=log_file)
    clear_log(log_path=log_file)
    entries = get_log(log_path=log_file)
    assert entries == []


def test_record_no_details(log_file):
    entry = record("export", log_path=log_file)
    assert entry["details"] == {}


def test_log_is_valid_json(log_file):
    record("lock", {"vault": ".env.vault"}, log_path=log_file)
    with open(log_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["action"] == "lock"
