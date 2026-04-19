"""Tests for envault.env_fmt."""
import pytest
from pathlib import Path

from envault.env_fmt import fmt_file, _normalize_line, FmtResult


@pytest.fixture
def env_file(tmp_path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p
    return _write


# --- unit tests for _normalize_line ---

def test_normalize_strips_spaces_around_value():
    assert _normalize_line("KEY= value ") == "KEY=value"


def test_normalize_strips_spaces_around_key():
    assert _normalize_line(" KEY =value") == "KEY=value"


def test_normalize_removes_unnecessary_double_quotes():
    assert _normalize_line('KEY="simplevalue"') == "KEY=simplevalue"


def test_normalize_removes_unnecessary_single_quotes():
    assert _normalize_line("KEY='simplevalue'") == "KEY=simplevalue"


def test_normalize_keeps_quotes_when_spaces_inside():
    assert _normalize_line('KEY="hello world"') == 'KEY="hello world"'


def test_normalize_preserves_comment_lines():
    assert _normalize_line("# a comment") == "# a comment"


def test_normalize_preserves_blank_lines():
    assert _normalize_line("") == ""


def test_normalize_no_equals_unchanged():
    assert _normalize_line("NOEQUALS") == "NOEQUALS"


# --- integration tests for fmt_file ---

def test_fmt_file_returns_fmt_result(env_file):
    p = env_file("KEY=value\n")
    result = fmt_file(p)
    assert isinstance(result, FmtResult)


def test_fmt_file_detects_changes(env_file):
    p = env_file('KEY = "simple"\n')
    result = fmt_file(p)
    assert result.changed_count == 1


def test_fmt_file_no_changes_for_clean_file(env_file):
    p = env_file("KEY=value\nOTHER=123\n")
    result = fmt_file(p)
    assert result.changed_count == 0


def test_fmt_file_write_false_does_not_modify(env_file):
    original = 'KEY = "val"\n'
    p = env_file(original)
    fmt_file(p, write=False)
    assert p.read_text() == original


def test_fmt_file_write_true_modifies_file(env_file):
    p = env_file('KEY = "val"\n')
    result = fmt_file(p, write=True)
    assert result.written is True
    assert p.read_text() == "KEY=val\n"


def test_fmt_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        fmt_file(tmp_path / "missing.env")
