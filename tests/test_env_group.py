"""Tests for env_group module and CLI."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.env_group import group_by_prefix, format_groups, GroupResult
from envault.cli_env_group import group_cmd


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_NAME=mydb\n"
        "AWS_KEY=abc\n"
        "AWS_SECRET=xyz\n"
        "APP_ENV=production\n"
        "STANDALONE=yes\n"
    )
    return f


def test_group_by_explicit_prefix(env_file):
    result = group_by_prefix(env_file, prefixes=["DB", "AWS"])
    assert "DB" in result.groups
    assert "AWS" in result.groups
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}
    assert set(result.groups["AWS"]) == {"AWS_KEY", "AWS_SECRET"}


def test_group_ungrouped_keys(env_file):
    result = group_by_prefix(env_file, prefixes=["DB"])
    assert "STANDALONE" in result.ungrouped
    assert "AWS_KEY" in result.ungrouped


def test_group_auto_detect(env_file):
    result = group_by_prefix(env_file)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_group_names_property(env_file):
    result = group_by_prefix(env_file, prefixes=["DB", "AWS"])
    assert set(result.group_names) == {"DB", "AWS"}


def test_group_returns_group_result_type(env_file):
    result = group_by_prefix(env_file, prefixes=["DB"])
    assert isinstance(result, GroupResult)


def test_format_groups_contains_prefix_header(env_file):
    result = group_by_prefix(env_file, prefixes=["DB"])
    output = format_groups(result)
    assert "[DB]" in output
    assert "DB_HOST=localhost" in output


def test_format_groups_ungrouped_section(env_file):
    result = group_by_prefix(env_file, prefixes=["DB"])
    output = format_groups(result)
    assert "[ungrouped]" in output


def test_cli_show_groups(env_file):
    runner = CliRunner()
    result = runner.invoke(group_cmd, ["show", str(env_file), "-p", "DB", "-p", "AWS"])
    assert result.exit_code == 0
    assert "[DB]" in result.output
    assert "[AWS]" in result.output


def test_cli_show_missing_file():
    runner = CliRunner()
    result = runner.invoke(group_cmd, ["show", "/nonexistent/.env"])
    assert result.exit_code != 0
