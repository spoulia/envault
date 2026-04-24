"""Tests for envault.env_count."""
import pytest
from pathlib import Path

from envault.env_count import (
    CountResult,
    count_file,
    count_many,
    format_count,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "# database settings\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_PASSWORD=\n"
        "\n"
        "# app settings\n"
        "APP_DEBUG=true\n"
        "APP_SECRET=supersecret\n"
        "STANDALONE=yes\n",
        encoding="utf-8",
    )
    return p


def test_count_returns_count_result_type(env_file: Path):
    result = count_file(env_file)
    assert isinstance(result, CountResult)


def test_total_keys(env_file: Path):
    result = count_file(env_file)
    assert result.total == 6


def test_set_keys(env_file: Path):
    result = count_file(env_file)
    assert result.set_keys == 5


def test_empty_keys(env_file: Path):
    result = count_file(env_file)
    assert result.empty_keys == 1


def test_comment_lines(env_file: Path):
    result = count_file(env_file)
    assert result.comment_lines == 2


def test_blank_lines(env_file: Path):
    result = count_file(env_file)
    assert result.blank_lines == 1


def test_per_prefix_groups(env_file: Path):
    result = count_file(env_file)
    assert result.per_prefix["DB"] == 3
    assert result.per_prefix["APP"] == 2


def test_per_prefix_no_underscore_key_excluded(env_file: Path):
    result = count_file(env_file)
    # STANDALONE has no underscore so should not appear in per_prefix
    assert "STANDALONE" not in result.per_prefix


def test_file_attribute(env_file: Path):
    result = count_file(env_file)
    assert str(env_file) == result.file


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        count_file(tmp_path / "nonexistent.env")


def test_count_many_returns_list(env_file: Path):
    results = count_many([env_file, env_file])
    assert len(results) == 2
    assert all(isinstance(r, CountResult) for r in results)


def test_format_count_contains_totals(env_file: Path):
    result = count_file(env_file)
    output = format_count(result)
    assert "Total keys" in output
    assert str(result.total) in output
    assert "DB_*" in output
