"""Tests for envault.env_sort."""
import pytest
from pathlib import Path
from envault.env_sort import sort_file, SortResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "ZEBRA=1\n"
        "APPLE=2\n"
        "MANGO=3\n"
    )
    return p


def test_sort_returns_sort_result(env_file):
    result = sort_file(env_file)
    assert isinstance(result, SortResult)


def test_sort_alphabetical(env_file):
    result = sort_file(env_file)
    assert result.sorted_order == ["apple", "mango", "zebra"]
    assert result.changed is True


def test_sort_writes_file(env_file):
    sort_file(env_file)
    lines = [l for l in env_file.read_text().splitlines() if l.strip()]
    keys = [l.split("=")[0] for l in lines]
    assert keys == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_reverse(env_file):
    result = sort_file(env_file, reverse=True)
    assert result.sorted_order == ["zebra", "mango", "apple"]


def test_sort_already_sorted_not_changed(tmp_path):
    p = tmp_path / ".env"
    p.write_text("ALPHA=1\nBETA=2\nGAMMA=3\n")
    result = sort_file(p)
    assert result.changed is False


def test_sort_dry_run_does_not_write(env_file):
    original = env_file.read_text()
    result = sort_file(env_file, dry_run=True)
    assert result.changed is True
    assert env_file.read_text() == original


def test_sort_preserves_comments(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "# zebra comment\n"
        "ZEBRA=1\n"
        "# apple comment\n"
        "APPLE=2\n"
    )
    sort_file(p)
    content = p.read_text()
    apple_pos = content.index("APPLE")
    zebra_pos = content.index("ZEBRA")
    apple_comment_pos = content.index("# apple comment")
    assert apple_comment_pos < apple_pos < zebra_pos


def test_sort_empty_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("")
    result = sort_file(p)
    assert result.changed is False
    assert result.sorted_order == []
