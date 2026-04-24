"""Tests for envault.env_freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_freeze import (
    FreezeResult,
    DriftResult,
    DriftIssue,
    freeze,
    check_drift,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("API_KEY=abc123\nDEBUG=true\nPORT=8080\n")
    return p


def test_freeze_returns_freeze_result_type(env_file: Path) -> None:
    result = freeze(env_file)
    assert isinstance(result, FreezeResult)


def test_freeze_keys_count(env_file: Path) -> None:
    result = freeze(env_file)
    assert result.keys_frozen == 3


def test_freeze_creates_file(env_file: Path) -> None:
    result = freeze(env_file)
    assert Path(result.freeze_file).exists()


def test_freeze_file_is_valid_json(env_file: Path) -> None:
    result = freeze(env_file)
    data = json.loads(Path(result.freeze_file).read_text())
    assert "snapshot" in data
    assert data["snapshot"]["API_KEY"] == "abc123"


def test_freeze_custom_output_path(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "custom_freeze.json"
    result = freeze(env_file, out)
    assert Path(result.freeze_file) == out
    assert out.exists()


def test_freeze_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        freeze(tmp_path / "nonexistent.env")


def test_check_drift_no_drift(env_file: Path) -> None:
    freeze(env_file)
    result = check_drift(env_file)
    assert isinstance(result, DriftResult)
    assert not result.has_drift
    assert result.issues == []


def test_check_drift_detects_changed(env_file: Path) -> None:
    freeze(env_file)
    env_file.write_text("API_KEY=NEWKEY\nDEBUG=true\nPORT=8080\n")
    result = check_drift(env_file)
    assert result.has_drift
    changed = [i for i in result.issues if i.kind == "changed"]
    assert any(i.key == "API_KEY" for i in changed)


def test_check_drift_detects_added(env_file: Path) -> None:
    freeze(env_file)
    env_file.write_text("API_KEY=abc123\nDEBUG=true\nPORT=8080\nNEW_VAR=hello\n")
    result = check_drift(env_file)
    added = [i for i in result.issues if i.kind == "added"]
    assert any(i.key == "NEW_VAR" for i in added)


def test_check_drift_detects_removed(env_file: Path) -> None:
    freeze(env_file)
    env_file.write_text("API_KEY=abc123\nDEBUG=true\n")
    result = check_drift(env_file)
    removed = [i for i in result.issues if i.kind == "removed"]
    assert any(i.key == "PORT" for i in removed)


def test_check_drift_missing_freeze_raises(env_file: Path, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        check_drift(env_file, tmp_path / "no_freeze.json")
