"""Tests for envault/cli_tags.py"""
import pytest
from click.testing import CliRunner
from envault import tags as tags_module
from envault.cli_tags import tags


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(tags_module, "TAGS_FILE", tmp_path / ".envault_tags.json")


@pytest.fixture
def runner():
    return CliRunner()


def test_add_tag_success(runner):
    result = runner.invoke(tags, ["add", "dev.vault", "backend"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_duplicate_tag_shows_error(runner):
    runner.invoke(tags, ["add", "dev.vault", "backend"])
    result = runner.invoke(tags, ["add", "dev.vault", "backend"])
    assert "Error" in result.output


def test_remove_tag_success(runner):
    runner.invoke(tags, ["add", "dev.vault", "temp"])
    result = runner.invoke(tags, ["remove", "dev.vault", "temp"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_tag_shows_error(runner):
    result = runner.invoke(tags, ["remove", "dev.vault", "ghost"])
    assert "Error" in result.output


def test_list_tags(runner):
    runner.invoke(tags, ["add", "dev.vault", "alpha"])
    runner.invoke(tags, ["add", "dev.vault", "beta"])
    result = runner.invoke(tags, ["list", "dev.vault"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_tags_empty(runner):
    result = runner.invoke(tags, ["list", "empty.vault"])
    assert "No tags" in result.output


def test_find_vaults_by_tag(runner):
    runner.invoke(tags, ["add", "a.vault", "prod"])
    runner.invoke(tags, ["add", "b.vault", "prod"])
    result = runner.invoke(tags, ["find", "prod"])
    assert "a.vault" in result.output
    assert "b.vault" in result.output


def test_clear_tags(runner):
    runner.invoke(tags, ["add", "dev.vault", "x"])
    result = runner.invoke(tags, ["clear", "dev.vault"])
    assert "cleared" in result.output
    list_result = runner.invoke(tags, ["list", "dev.vault"])
    assert "No tags" in list_result.output
