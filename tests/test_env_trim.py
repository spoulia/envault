"""Tests for envault.env_trim."""
import pytest
from pathlib import Path

from envault.env_trim import trim_file, TrimResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "API_KEY=first\n"
        "DB_HOST=localhost\n"
        "API_KEY=second\n"
        "SECRET=abc\n"
        "DB_HOST=remotehost\n"
    )
    return p


def test_trim_removes_duplicates(env_file):
    result = trim_file(env_file)
    assert "API_KEY" in result.removed
    assert "DB_HOST" in result.removed
    assert result.removed_count == 2


def test_trim_keeps_last_occurrence(env_file):
    trim_file(env_file)
    text = env_file.read_text()
    lines = [l for l in text.splitlines() if l.startswith("API_KEY")]
    assert len(lines) == 1
    assert lines[0] == "API_KEY=second"


def test_trim_returns_trim_result_type(env_file):
    result = trim_file(env_file)
    assert isinstance(result, TrimResult)


def test_trim_no_duplicates(tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\nB=2\nC=3\n")
    result = trim_file(p)
    assert result.removed_count == 0
    assert result.kept_count == 3


def test_trim_dry_run_does_not_modify(env_file):
    original = env_file.read_text()
    result = trim_file(env_file, dry_run=True)
    assert result.removed_count == 2
    assert env_file.read_text() == original


def test_trim_preserves_comments(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# comment\nA=1\nA=2\n")
    trim_file(p)
    text = p.read_text()
    assert "# comment" in text
    assert "A=2" in text


def test_trim_original_path_set(env_file):
    result = trim_file(env_file)
    assert result.original_path == str(env_file)
