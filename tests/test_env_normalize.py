"""Tests for envault.env_normalize."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_normalize import (
    NormalizeResult,
    _normalize_key,
    _normalize_value,
    normalize_file,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        'db_host = "localhost"\n'
        'DB_PORT=5432\n'
        '# a comment\n'
        'api_key  =  "secret"\n',
        encoding="utf-8",
    )
    return p


def test_normalize_key_uppercases():
    assert _normalize_key("db_host") == "DB_HOST"


def test_normalize_key_strips_spaces():
    assert _normalize_key("  my_key  ") == "MY_KEY"


def test_normalize_value_strips_redundant_double_quotes():
    assert _normalize_value('"localhost"') == "localhost"


def test_normalize_value_strips_redundant_single_quotes():
    assert _normalize_value("'hello'") == "hello"


def test_normalize_value_keeps_quotes_when_inner_quote_present():
    assert _normalize_value('"it\'s here"') == '"it\'s here"'


def test_normalize_value_strips_surrounding_whitespace():
    assert _normalize_value("  value  ") == "value"


def test_normalize_file_returns_normalize_result_type(env_file: Path):
    result = normalize_file(env_file, dry_run=True)
    assert isinstance(result, NormalizeResult)


def test_normalize_file_detects_changes(env_file: Path):
    result = normalize_file(env_file, dry_run=True)
    assert result.changed
    assert result.changed_count > 0


def test_normalize_file_dry_run_does_not_write(env_file: Path):
    original = env_file.read_text(encoding="utf-8")
    normalize_file(env_file, dry_run=True)
    assert env_file.read_text(encoding="utf-8") == original


def test_normalize_file_writes_when_not_dry_run(env_file: Path):
    normalize_file(env_file, dry_run=False)
    content = env_file.read_text(encoding="utf-8")
    assert "db_host" not in content
    assert "DB_HOST" in content


def test_normalize_file_already_clean_has_no_changes(tmp_path: Path):
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\n", encoding="utf-8")
    result = normalize_file(p)
    assert not result.changed
    assert result.changed_count == 0


def test_normalize_file_comments_are_untouched(env_file: Path):
    result = normalize_file(env_file, dry_run=True)
    comment_lines = [l for l in result.normalized_lines if l.lstrip().startswith("#")]
    assert any("a comment" in l for l in comment_lines)


def test_normalize_file_change_records_line_number(env_file: Path):
    result = normalize_file(env_file, dry_run=True)
    line_numbers = [c[0] for c in result.changes]
    assert all(isinstance(n, int) and n >= 1 for n in line_numbers)
