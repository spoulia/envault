"""Tests for envault.env_comment."""
import pytest
from pathlib import Path
from envault.env_comment import get_comments, set_comment, remove_comment


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432  # default postgres port\n"
        "SECRET_KEY=abc123\n"
    )
    return p


def test_get_comments_returns_existing(env_file):
    comments = get_comments(env_file)
    assert comments == {"DB_PORT": "default postgres port"}


def test_get_comments_empty_when_none(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    assert get_comments(p) == {}


def test_set_comment_adds_new(env_file):
    result = set_comment(env_file, "DB_HOST", "primary host")
    assert "DB_HOST" in result.updated
    assert result.not_found == []
    comments = get_comments(env_file)
    assert comments["DB_HOST"] == "primary host"


def test_set_comment_overwrites_existing(env_file):
    result = set_comment(env_file, "DB_PORT", "updated comment", overwrite=True)
    assert "DB_PORT" in result.updated
    assert get_comments(env_file)["DB_PORT"] == "updated comment"


def test_set_comment_skips_when_no_overwrite(env_file):
    result = set_comment(env_file, "DB_PORT", "should not appear", overwrite=False)
    assert "DB_PORT" in result.skipped
    assert get_comments(env_file)["DB_PORT"] == "default postgres port"


def test_set_comment_key_not_found(env_file):
    result = set_comment(env_file, "MISSING_KEY", "some comment")
    assert "MISSING_KEY" in result.not_found
    assert result.updated == []


def test_remove_comment_strips_inline(env_file):
    result = remove_comment(env_file, "DB_PORT")
    assert "DB_PORT" in result.updated
    assert get_comments(env_file) == {}
    content = env_file.read_text()
    assert "DB_PORT=5432" in content
    assert "#" not in content.split("\n")[1]


def test_remove_comment_key_not_found(env_file):
    result = remove_comment(env_file, "NONEXISTENT")
    assert "NONEXISTENT" in result.not_found


def test_set_comment_preserves_other_lines(env_file):
    set_comment(env_file, "SECRET_KEY", "keep secret")
    content = env_file.read_text()
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content
