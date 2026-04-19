"""Tests for envault.env_split and cli_env_split."""
import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from envault.env_split import split_by_prefix, SplitResult
from envault.cli_env_split import split_cmd


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "AWS_KEY=abc\n"
        "AWS_SECRET=xyz\n"
        "APP_DEBUG=true\n"
        "UNTAGGED=value\n"
    )
    return p


def test_split_by_prefix_creates_files(env_file, tmp_path):
    out = tmp_path / "out"
    result = split_by_prefix(env_file, out, ["DB_", "AWS_"])
    assert (out / "db_.env").exists() or (out / "db.env").exists() or any("db" in f for f in result.files_written)
    assert result.keys_split == 4


def test_split_result_type(env_file, tmp_path):
    result = split_by_prefix(env_file, tmp_path / "out", ["DB_"])
    assert isinstance(result, SplitResult)


def test_split_unmatched_count(env_file, tmp_path):
    result = split_by_prefix(env_file, tmp_path / "out", ["DB_"])
    assert result.keys_unmatched == 4  # AWS_KEY, AWS_SECRET, APP_DEBUG, UNTAGGED


def test_split_remainder_file(env_file, tmp_path):
    out = tmp_path / "out"
    result = split_by_prefix(env_file, out, ["DB_"], remainder_file="rest.env")
    assert (out / "rest.env").exists()
    assert str(out / "rest.env") in result.files_written


def test_split_content_correct(env_file, tmp_path):
    out = tmp_path / "out"
    split_by_prefix(env_file, out, ["DB_"])
    db_file = out / "db_.env"
    content = db_file.read_text()
    assert "DB_HOST=localhost" in content
    assert "DB_PORT=5432" in content
    assert "AWS_KEY" not in content


def test_split_no_match_writes_nothing(env_file, tmp_path):
    out = tmp_path / "out"
    result = split_by_prefix(env_file, out, ["NOMATCH_"])
    assert result.files_written == []
    assert result.keys_split == 0


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_split_success(runner, env_file, tmp_path):
    out = tmp_path / "out"
    r = runner.invoke(split_cmd, ["run", str(env_file), "-p", "DB_", "-o", str(out)])
    assert r.exit_code == 0
    assert "Split" in r.output


def test_cli_split_no_match_message(runner, env_file, tmp_path):
    out = tmp_path / "out"
    r = runner.invoke(split_cmd, ["run", str(env_file), "-p", "NOMATCH_", "-o", str(out)])
    assert r.exit_code == 0
    assert "Nothing written" in r.output


def test_cli_split_remainder_flag(runner, env_file, tmp_path):
    out = tmp_path / "out"
    r = runner.invoke(split_cmd, ["run", str(env_file), "-p", "DB_", "-o", str(out), "--remainder", "rest.env"])
    assert r.exit_code == 0
    assert (out / "rest.env").exists()
