"""Tests for envault/env_scope.py"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_scope import (
    ScopeResult,
    assign_scope,
    get_scope,
    keys_for_scope,
    list_scopes,
    remove_scope,
)


@pytest.fixture()
def scope_file(tmp_path) -> Path:
    return tmp_path / "scopes.json"


def test_assign_scope_creates_entry(scope_file):
    result = assign_scope("DB_URL", ["prod"], path=scope_file)
    assert "prod" in result.scopes


def test_assign_scope_persists(scope_file):
    assign_scope("DB_URL", ["dev"], path=scope_file)
    data = json.loads(scope_file.read_text())
    assert "dev" in data["DB_URL"]


def test_assign_scope_returns_scope_result_type(scope_file):
    result = assign_scope("KEY", ["staging"], path=scope_file)
    assert isinstance(result, ScopeResult)


def test_assign_scope_accumulates(scope_file):
    assign_scope("KEY", ["dev"], path=scope_file)
    result = assign_scope("KEY", ["prod"], path=scope_file)
    assert "dev" in result.scopes
    assert "prod" in result.scopes


def test_assign_invalid_scope_raises(scope_file):
    with pytest.raises(ValueError, match="Unknown scope"):
        assign_scope("KEY", ["nightly"], path=scope_file)


def test_remove_scope_removes_entry(scope_file):
    assign_scope("KEY", ["dev", "prod"], path=scope_file)
    result = remove_scope("KEY", ["dev"], path=scope_file)
    assert "dev" not in result.scopes
    assert "prod" in result.scopes


def test_get_scope_returns_empty_for_unknown_key(scope_file):
    result = get_scope("MISSING", path=scope_file)
    assert result.scopes == []


def test_get_scope_returns_assigned_scopes(scope_file):
    assign_scope("API_KEY", ["staging", "prod"], path=scope_file)
    result = get_scope("API_KEY", path=scope_file)
    assert sorted(result.scopes) == ["prod", "staging"]


def test_list_scopes_empty_when_no_file(scope_file):
    assert list_scopes(path=scope_file) == {}


def test_list_scopes_returns_all(scope_file):
    assign_scope("A", ["dev"], path=scope_file)
    assign_scope("B", ["prod"], path=scope_file)
    registry = list_scopes(path=scope_file)
    assert "A" in registry
    assert "B" in registry


def test_keys_for_scope_returns_matching_keys(scope_file):
    assign_scope("DB_URL", ["prod"], path=scope_file)
    assign_scope("DEBUG", ["dev"], path=scope_file)
    assign_scope("SECRET", ["dev", "prod"], path=scope_file)
    keys = keys_for_scope("prod", path=scope_file)
    assert "DB_URL" in keys
    assert "SECRET" in keys
    assert "DEBUG" not in keys


def test_scope_count_property(scope_file):
    result = assign_scope("KEY", ["dev", "staging", "prod"], path=scope_file)
    assert result.scope_count == 3
