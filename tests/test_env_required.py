"""Tests for envault.env_required."""
from pathlib import Path

import pytest

from envault.env_required import RequiredResult, check_required, has_issues


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=\nAPI_KEY=abc123\n")
    return p


def test_all_required_keys_present(env_file: Path):
    result = check_required(env_file, ["DB_HOST", "API_KEY"])
    assert not has_issues(result)


def test_returns_required_result_type(env_file: Path):
    result = check_required(env_file, ["DB_HOST"])
    assert isinstance(result, RequiredResult)


def test_missing_key_is_reported(env_file: Path):
    result = check_required(env_file, ["MISSING_KEY"])
    assert has_issues(result)
    assert result.issues[0].key == "MISSING_KEY"
    assert result.issues[0].reason == "missing"


def test_empty_value_is_reported_by_default(env_file: Path):
    result = check_required(env_file, ["SECRET"])
    assert has_issues(result)
    assert result.issues[0].reason == "empty"


def test_allow_empty_suppresses_empty_issue(env_file: Path):
    result = check_required(env_file, ["SECRET"], allow_empty=True)
    assert not has_issues(result)


def test_checked_list_matches_input(env_file: Path):
    keys = ["DB_HOST", "API_KEY"]
    result = check_required(env_file, keys)
    assert result.checked == keys


def test_missing_file_reports_all_keys_missing(tmp_path: Path):
    missing = tmp_path / "nonexistent.env"
    result = check_required(missing, ["A", "B"])
    assert len(result.issues) == 2
    assert all(i.reason == "missing" for i in result.issues)


def test_multiple_issues_reported(env_file: Path):
    result = check_required(env_file, ["SECRET", "MISSING_KEY"])
    reasons = {i.key: i.reason for i in result.issues}
    assert reasons["SECRET"] == "empty"
    assert reasons["MISSING_KEY"] == "missing"
