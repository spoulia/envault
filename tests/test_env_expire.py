"""Tests for envault.env_expire and envault.cli_env_expire."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_expire import (
    ExpiryEntry,
    ExpiryResult,
    ExpiredResult,
    add_expiry,
    check_expiry,
    list_expiries,
    remove_expiry,
)
from envault.cli_env_expire import expire_cmd


@pytest.fixture()
def reg(tmp_path: Path) -> Path:
    return tmp_path / "expiry.json"


# ── unit tests ────────────────────────────────────────────────────────────────

def test_add_expiry_returns_entry(reg):
    entry = add_expiry("API_KEY", "2099-01-01", registry=reg)
    assert isinstance(entry, ExpiryEntry)
    assert entry.key == "API_KEY"
    assert entry.expires_on == "2099-01-01"


def test_add_expiry_persists(reg):
    add_expiry("DB_PASS", "2099-06-30", registry=reg)
    result = list_expiries(reg)
    assert any(e.key == "DB_PASS" for e in result.entries)


def test_add_duplicate_raises(reg):
    add_expiry("TOKEN", "2099-01-01", registry=reg)
    with pytest.raises(ValueError, match="already exists"):
        add_expiry("TOKEN", "2099-02-01", registry=reg)


def test_add_invalid_date_raises(reg):
    with pytest.raises(ValueError, match="Invalid date"):
        add_expiry("BAD", "not-a-date", registry=reg)


def test_remove_expiry_returns_true(reg):
    add_expiry("X", "2099-01-01", registry=reg)
    assert remove_expiry("X", reg) is True


def test_remove_missing_returns_false(reg):
    assert remove_expiry("GHOST", reg) is False


def test_list_expiries_returns_result_type(reg):
    result = list_expiries(reg)
    assert isinstance(result, ExpiryResult)


def test_list_empty_when_no_file(reg):
    result = list_expiries(reg)
    assert result.count == 0


def test_check_expiry_detects_expired(reg):
    add_expiry("OLD_KEY", "2000-01-01", registry=reg)
    result = check_expiry(registry=reg)
    assert isinstance(result, ExpiredResult)
    assert result.has_expired
    assert any(e.key == "OLD_KEY" for e in result.expired)


def test_check_expiry_detects_upcoming(reg):
    add_expiry("SOON_KEY", "2099-12-31", registry=reg)
    # Treat everything as upcoming by using a huge warn_days window
    result = check_expiry(warn_days=999999, registry=reg)
    assert any(e.key == "SOON_KEY" for e in result.upcoming)


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_add_success(runner, reg):
    res = runner.invoke(expire_cmd, ["add", "MY_KEY", "2099-03-15", "--registry", str(reg)])
    assert res.exit_code == 0
    assert "Registered" in res.output


def test_cli_add_invalid_date_shows_error(runner, reg):
    res = runner.invoke(expire_cmd, ["add", "K", "bad-date", "--registry", str(reg)])
    assert res.exit_code == 1


def test_cli_list_shows_entries(runner, reg):
    add_expiry("LISTED", "2099-07-04", registry=reg)
    res = runner.invoke(expire_cmd, ["list", "--registry", str(reg)])
    assert "LISTED" in res.output


def test_cli_check_expired_exits_nonzero(runner, reg):
    add_expiry("STALE", "2000-01-01", registry=reg)
    res = runner.invoke(expire_cmd, ["check", "--registry", str(reg)])
    assert res.exit_code == 1
    assert "EXPIRED" in res.output


def test_cli_check_clean_exits_zero(runner, reg):
    res = runner.invoke(expire_cmd, ["check", "--registry", str(reg)])
    assert res.exit_code == 0
