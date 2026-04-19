"""Tests for envault.env_head."""
from pathlib import Path

import pytest

from envault.env_head import HeadResult, format_head, head_file


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "ALPHA=1\n"
        "BETA=2\n"
        "GAMMA=3\n"
        "DELTA=4\n"
        "EPSILON=5\n"
    )
    return f


def test_head_returns_head_result_type(env_file: Path) -> None:
    result = head_file(env_file, n=3)
    assert isinstance(result, HeadResult)


def test_head_default_n_returns_all_when_fewer(env_file: Path) -> None:
    result = head_file(env_file, n=10)
    assert result.shown == 5
    assert result.total_keys == 5


def test_head_limits_to_n(env_file: Path) -> None:
    result = head_file(env_file, n=2)
    assert result.shown == 2
    assert result.lines[0] == ("ALPHA", "1")
    assert result.lines[1] == ("BETA", "2")


def test_head_total_keys_is_full_count(env_file: Path) -> None:
    result = head_file(env_file, n=2)
    assert result.total_keys == 5


def test_head_skips_comments_and_blanks(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("# comment\n\nFOO=bar\nBAZ=qux\n")
    result = head_file(f, n=5)
    assert result.total_keys == 2
    assert result.lines[0] == ("FOO", "bar")


def test_head_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        head_file(tmp_path / "missing.env", n=5)


def test_head_invalid_n_raises(env_file: Path) -> None:
    with pytest.raises(ValueError):
        head_file(env_file, n=0)


def test_format_head_shows_truncation_message(env_file: Path) -> None:
    result = head_file(env_file, n=2)
    output = format_head(result)
    assert "3 more key(s) not shown" in output


def test_format_head_no_truncation_when_all_shown(env_file: Path) -> None:
    result = head_file(env_file, n=10)
    output = format_head(result)
    assert "not shown" not in output


def test_format_head_empty_file(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("")
    result = head_file(f, n=5)
    assert format_head(result) == "(no keys)"
