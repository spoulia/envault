"""Tests for env_grep module."""
import pytest
from pathlib import Path
from envault.env_grep import grep_files, format_grep, GrepResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DATABASE_URL=postgres://localhost/db\n"
        "SECRET_KEY=supersecret\n"
        "DEBUG=true\n"
        "# a comment\n"
        "EMPTY=\n"
        "API_TOKEN=abc123\n"
    )
    return p


def test_grep_returns_grep_result_type(env_file):
    result = grep_files([env_file], "DEBUG")
    assert isinstance(result, GrepResult)


def test_grep_finds_key_match(env_file):
    result = grep_files([env_file], "SECRET")
    assert result.match_count == 1
    assert result.matches[0].key == "SECRET_KEY"


def test_grep_finds_value_match(env_file):
    result = grep_files([env_file], "postgres")
    assert result.match_count == 1
    assert result.matches[0].key == "DATABASE_URL"


def test_grep_no_match_returns_empty(env_file):
    result = grep_files([env_file], "NONEXISTENT")
    assert result.match_count == 0


def test_grep_ignore_case(env_file):
    result = grep_files([env_file], "debug", ignore_case=True)
    assert result.match_count == 1


def test_grep_keys_only(env_file):
    result = grep_files([env_file], "abc123", search_values=False, search_keys=True)
    assert result.match_count == 0


def test_grep_values_only(env_file):
    result = grep_files([env_file], "API", search_values=True, search_keys=False)
    assert result.match_count == 0


def test_grep_files_searched_count(env_file, tmp_path):
    other = tmp_path / ".env.prod"
    other.write_text("FOO=bar\n")
    result = grep_files([env_file, other], "FOO")
    assert result.files_searched == 2


def test_grep_missing_file_skipped(tmp_path):
    result = grep_files([tmp_path / "missing.env"], "KEY")
    assert result.files_searched == 0
    assert result.match_count == 0


def test_grep_invalid_pattern_raises(env_file):
    with pytest.raises(ValueError, match="Invalid regex"):
        grep_files([env_file], "[invalid")


def test_format_grep_no_matches():
    result = GrepResult(pattern="X")
    assert "No matches" in format_grep(result)


def test_format_grep_shows_file_and_key(env_file):
    result = grep_files([env_file], "DEBUG")
    output = format_grep(result)
    assert "DEBUG" in output
    assert str(env_file) in output


def test_format_grep_show_values(env_file):
    result = grep_files([env_file], "DEBUG")
    output = format_grep(result, show_values=True)
    assert "true" in output
