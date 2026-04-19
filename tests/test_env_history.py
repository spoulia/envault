"""Tests for envault.env_history."""
import time
import pytest
from pathlib import Path

from envault.env_history import (
    record_change,
    get_history,
    clear_history,
    HistoryResult,
    HistoryEntry,
)


@pytest.fixture
def hfile(tmp_path):
    return tmp_path / "history.json"


def test_record_creates_entry(hfile):
    e = record_change("set", "API_KEY", old_value=None, new_value="abc", history_file=hfile)
    assert isinstance(e, HistoryEntry)
    assert e.key == "API_KEY"
    assert e.action == "set"
    assert e.new_value == "abc"


def test_record_persists(hfile):
    record_change("set", "DB_URL", new_value="postgres://", history_file=hfile)
    result = get_history(history_file=hfile)
    assert result.count == 1
    assert result.entries[0].key == "DB_URL"


def test_get_history_empty_when_no_file(hfile):
    result = get_history(history_file=hfile)
    assert isinstance(result, HistoryResult)
    assert result.count == 0


def test_get_history_filter_by_key(hfile):
    record_change("set", "KEY_A", new_value="1", history_file=hfile)
    record_change("set", "KEY_B", new_value="2", history_file=hfile)
    result = get_history(key="KEY_A", history_file=hfile)
    assert result.count == 1
    assert result.entries[0].key == "KEY_A"


def test_get_history_last_limits(hfile):
    for i in range(5):
        record_change("set", f"K{i}", new_value=str(i), history_file=hfile)
    result = get_history(last=3, history_file=hfile)
    assert result.count == 3
    assert result.entries[-1].key == "K4"


def test_clear_history_removes_all(hfile):
    record_change("set", "X", new_value="1", history_file=hfile)
    clear_history(history_file=hfile)
    result = get_history(history_file=hfile)
    assert result.count == 0


def test_entry_has_timestamp(hfile):
    before = time.time()
    e = record_change("unset", "OLD_KEY", old_value="v", history_file=hfile)
    after = time.time()
    assert before <= e.timestamp <= after


def test_record_with_note(hfile):
    e = record_change("set", "TOKEN", new_value="x", note="rotation", history_file=hfile)
    assert e.note == "rotation"
    result = get_history(history_file=hfile)
    assert result.entries[0].note == "rotation"
