"""Tests for envault.lint."""
import pytest
from pathlib import Path
from envault.lint import lint_file, LintResult


@pytest.fixture
def env_file(tmp_path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p
    return _write


def test_clean_file_has_no_issues(env_file):
    p = env_file("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\n")
    result = lint_file(p)
    assert result.ok
    assert result.issues == []


def test_missing_separator_is_error(env_file):
    p = env_file("BADLINE\n")
    result = lint_file(p)
    assert not result.ok
    assert any(i.message == "Missing '=' separator" for i in result.issues)


def test_lowercase_key_is_warning(env_file):
    p = env_file("my_key=value\n")
    result = lint_file(p)
    assert any(i.severity == "warning" and "uppercase" in i.message for i in result.issues)
    assert result.ok  # only warning, not error


def test_empty_value_is_warning(env_file):
    p = env_file("SECRET=\n")
    result = lint_file(p)
    assert any(i.severity == "warning" and "Empty value" in i.message for i in result.issues)


def test_duplicate_key_is_error(env_file):
    p = env_file("FOO=bar\nFOO=baz\n")
    result = lint_file(p)
    assert not result.ok
    assert any("Duplicate key" in i.message for i in result.issues)


def test_key_with_spaces_is_error(env_file):
    p = env_file("MY KEY=value\n")
    result = lint_file(p)
    assert any(i.severity == "error" and "spaces" in i.message for i in result.issues)


def test_comments_and_blank_lines_ignored(env_file):
    p = env_file("# comment\n\nFOO=bar\n")
    result = lint_file(p)
    assert result.issues == []


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        lint_file(tmp_path / "nonexistent.env")
