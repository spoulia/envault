"""Tests for envault.env_unique."""
import pytest
from pathlib import Path
from envault.env_unique import find_duplicate_values, format_unique, UniqueResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_PASS=secret\n"
        "API_KEY=secret\n"
        "TOKEN=abc123\n"
        "SECRET=secret\n"
        "PORT=8080\n"
        "DEBUG_PORT=8080\n"
    )
    return p


def test_find_duplicate_values_returns_type(env_file):
    result = find_duplicate_values(env_file)
    assert isinstance(result, UniqueResult)


def test_detects_shared_values(env_file):
    result = find_duplicate_values(env_file)
    assert "secret" in result.duplicates
    assert set(result.duplicates["secret"]) == {"DB_PASS", "API_KEY", "SECRET"}


def test_detects_multiple_duplicate_groups(env_file):
    result = find_duplicate_values(env_file)
    assert "8080" in result.duplicates
    assert set(result.duplicates["8080"]) == {"PORT", "DEBUG_PORT"}


def test_total_keys_count(env_file):
    result = find_duplicate_values(env_file)
    assert result.total_keys == 6


def test_unique_values_count(env_file):
    result = find_duplicate_values(env_file)
    # secret, abc123, 8080 -> 3 distinct values
    assert result.unique_values == 3


def test_no_duplicates(tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\nB=2\nC=3\n")
    result = find_duplicate_values(p)
    assert not result.has_duplicates


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_duplicate_values(tmp_path / "missing.env")


def test_format_no_duplicates(tmp_path):
    p = tmp_path / ".env"
    p.write_text("X=one\nY=two\n")
    result = find_duplicate_values(p)
    assert format_unique(result) == "All values are unique."


def test_format_shows_duplicate_keys(env_file):
    result = find_duplicate_values(env_file)
    output = format_unique(result)
    assert "Duplicate values found:" in output
    assert "DB_PASS" in output
    assert "API_KEY" in output


def test_comments_and_blank_lines_ignored(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# comment\n\nA=val\nB=val\n")
    result = find_duplicate_values(p)
    assert result.total_keys == 2
    assert "val" in result.duplicates
