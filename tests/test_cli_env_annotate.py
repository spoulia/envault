"""Tests for envault/cli_env_annotate.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_annotate import annotate_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def isolated(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _ann_file(base: Path) -> str:
    return str(base / "annotations.json")


def test_add_annotation_success(runner, isolated):
    result = runner.invoke(
        annotate_cmd, ["add", "DB_HOST", "Primary host", "--file", _ann_file(isolated)]
    )
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_add_annotation_with_author_and_tag(runner, isolated):
    result = runner.invoke(
        annotate_cmd,
        ["add", "SECRET_KEY", "Django secret", "--author", "alice", "--tag", "security", "--file", _ann_file(isolated)],
    )
    assert result.exit_code == 0
    data = json.loads(Path(_ann_file(isolated)).read_text())
    assert data["SECRET_KEY"]["author"] == "alice"
    assert "security" in data["SECRET_KEY"]["tags"]


def test_add_duplicate_annotation_shows_error(runner, isolated):
    f = _ann_file(isolated)
    runner.invoke(annotate_cmd, ["add", "DB_HOST", "First", "--file", f])
    result = runner.invoke(annotate_cmd, ["add", "DB_HOST", "Second", "--file", f])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_update_annotation_success(runner, isolated):
    f = _ann_file(isolated)
    runner.invoke(annotate_cmd, ["add", "DB_HOST", "Old note", "--file", f])
    result = runner.invoke(annotate_cmd, ["update", "DB_HOST", "New note", "--file", f])
    assert result.exit_code == 0
    assert "updated" in result.output.lower()


def test_remove_annotation_success(runner, isolated):
    f = _ann_file(isolated)
    runner.invoke(annotate_cmd, ["add", "DB_HOST", "Some note", "--file", f])
    result = runner.invoke(annotate_cmd, ["remove", "DB_HOST", "--file", f])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_list_annotations_shows_entries(runner, isolated):
    f = _ann_file(isolated)
    runner.invoke(annotate_cmd, ["add", "DB_HOST", "Host note", "--file", f])
    runner.invoke(annotate_cmd, ["add", "DB_PORT", "Port note", "--file", f])
    result = runner.invoke(annotate_cmd, ["list", "--file", f])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output


def test_list_empty_annotations(runner, isolated):
    result = runner.invoke(annotate_cmd, ["list", "--file", _ann_file(isolated)])
    assert result.exit_code == 0
    assert "No annotations" in result.output
