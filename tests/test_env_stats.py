"""Tests for envault.env_stats and envault.cli_env_stats."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_stats import compute_stats
from envault.cli_env_stats import stats


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text(
        "# database settings\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_PASSWORD=\n"
        "DB_PASSWORD=secret\n"  # duplicate
        "API_KEY=<YOUR_API_KEY>\n"
        "API_SECRET=CHANGEME\n"
        "\n"
        "APP_DEBUG=true\n"
    )
    return f


def test_total_keys(env_file):
    r = compute_stats(env_file)
    assert r.total_keys == 7


def test_empty_values(env_file):
    r = compute_stats(env_file)
    assert r.empty_values == 1


def test_placeholder_values(env_file):
    r = compute_stats(env_file)
    assert r.placeholder_values == 2


def test_comment_lines(env_file):
    r = compute_stats(env_file)
    assert r.comment_lines == 1


def test_blank_lines(env_file):
    r = compute_stats(env_file)
    assert r.blank_lines == 1


def test_duplicate_keys(env_file):
    r = compute_stats(env_file)
    assert "DB_PASSWORD" in r.duplicate_keys


def test_prefix_counts(env_file):
    r = compute_stats(env_file)
    assert r.prefix_counts["DB"] == 4
    assert r.prefix_counts["API"] == 2


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        compute_stats(tmp_path / "missing.env")


def test_cli_show(env_file):
    runner = CliRunner()
    result = runner.invoke(stats, ["show", str(env_file)])
    assert result.exit_code == 0
    assert "Total keys" in result.output
    assert "Duplicate keys" in result.output


def test_cli_show_prefixes(env_file):
    runner = CliRunner()
    result = runner.invoke(stats, ["show", str(env_file), "--prefixes"])
    assert result.exit_code == 0
    assert "DB" in result.output
    assert "API" in result.output
