"""Tests for envault.env_mask_policy."""
from __future__ import annotations

import pytest

from envault.env_mask_policy import (
    PolicyResult,
    add_policy,
    enforce_policy,
    list_policies,
    remove_policy,
)


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    policy_file = tmp_path / ".envault" / "mask_policy.json"
    import envault.env_mask_policy as _mod
    monkeypatch.setattr(_mod, "_DEFAULT_POLICY_FILE", policy_file)
    return policy_file


def test_add_policy_creates_entry(isolated):
    entry = add_policy("SECRET", "mask", policy_file=isolated)
    assert entry.pattern == "SECRET"
    assert entry.action == "mask"


def test_add_policy_persists(isolated):
    add_policy("TOKEN", "block", policy_file=isolated)
    entries = list_policies(policy_file=isolated)
    assert any(e.pattern == "TOKEN" for e in entries)


def test_add_duplicate_raises(isolated):
    add_policy("KEY", "mask", policy_file=isolated)
    with pytest.raises(ValueError, match="already exists"):
        add_policy("KEY", "allow", policy_file=isolated)


def test_add_invalid_action_raises(isolated):
    with pytest.raises(ValueError, match="Invalid action"):
        add_policy("FOO", "delete", policy_file=isolated)


def test_remove_policy_returns_true(isolated):
    add_policy("PASS", "block", policy_file=isolated)
    assert remove_policy("PASS", policy_file=isolated) is True


def test_remove_missing_policy_returns_false(isolated):
    assert remove_policy("NONEXISTENT", policy_file=isolated) is False


def test_list_policies_empty_when_no_file(isolated):
    assert list_policies(policy_file=isolated) == []


def test_enforce_policy_returns_policy_result_type(isolated):
    result = enforce_policy({"DB_PASSWORD": "secret"}, policy_file=isolated)
    assert isinstance(result, PolicyResult)


def test_enforce_block_action_creates_violation(isolated):
    add_policy("PASSWORD", "block", policy_file=isolated)
    result = enforce_policy({"DB_PASSWORD": "secret"}, policy_file=isolated)
    assert result.has_violations
    assert "DB_PASSWORD" in result.violations


def test_enforce_mask_action_no_violation(isolated):
    add_policy("SECRET", "mask", policy_file=isolated)
    result = enforce_policy({"API_SECRET": "abc123"}, policy_file=isolated)
    assert not result.has_violations


def test_enforce_allow_action_no_violation(isolated):
    add_policy("TOKEN", "allow", policy_file=isolated)
    result = enforce_policy({"AUTH_TOKEN": "xyz"}, policy_file=isolated)
    assert not result.has_violations


def test_enforce_no_policies_no_violations(isolated):
    result = enforce_policy({"ANY_KEY": "value"}, policy_file=isolated)
    assert not result.has_violations
