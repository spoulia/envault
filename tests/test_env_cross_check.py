"""Tests for envault.env_cross_check."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_cross_check import (
    CrossCheckResult,
    cross_check,
    format_cross_check,
    has_issues,
)
from envault.cli_env_cross_check import cross_check_cmd


@pytest.fixture()
def env_dir(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Unit tests – env_cross_check module
# ---------------------------------------------------------------------------

def test_cross_check_returns_result_type(env_dir):
    ref = _write(env_dir / "ref.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    tgt = _write(env_dir / "tgt.env", "DB_HOST=prod.db\nDB_PORT=5432\n")
    result = cross_check(ref, tgt)
    assert isinstance(result, CrossCheckResult)


def test_cross_check_all_present_no_issues(env_dir):
    ref = _write(env_dir / "ref.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    tgt = _write(env_dir / "tgt.env", "DB_HOST=prod.db\nDB_PORT=5432\n")
    result = cross_check(ref, tgt)
    assert not has_issues(result)
    assert result.checked == 2


def test_cross_check_detects_missing_key(env_dir):
    ref = _write(env_dir / "ref.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    tgt = _write(env_dir / "tgt.env", "DB_HOST=prod.db\n")
    result = cross_check(ref, tgt)
    assert has_issues(result)
    kinds = [i.kind for i in result.issues]
    assert "missing" in kinds


def test_cross_check_detects_empty_value(env_dir):
    ref = _write(env_dir / "ref.env", "API_KEY=secret\n")
    tgt = _write(env_dir / "tgt.env", "API_KEY=\n")
    result = cross_check(ref, tgt)
    assert has_issues(result)
    assert result.issues[0].kind == "empty"


def test_cross_check_allow_empty_skips_empty_check(env_dir):
    ref = _write(env_dir / "ref.env", "API_KEY=secret\n")
    tgt = _write(env_dir / "tgt.env", "API_KEY=\n")
    result = cross_check(ref, tgt, allow_empty=True)
    assert not has_issues(result)


def test_cross_check_specific_keys_only(env_dir):
    ref = _write(env_dir / "ref.env", "A=1\nB=2\nC=3\n")
    tgt = _write(env_dir / "tgt.env", "A=x\n")
    result = cross_check(ref, tgt, keys=["A"])
    assert not has_issues(result)
    assert result.checked == 1


def test_cross_check_missing_reference_raises(env_dir):
    tgt = _write(env_dir / "tgt.env", "A=1\n")
    with pytest.raises(FileNotFoundError):
        cross_check(env_dir / "ghost.env", tgt)


def test_format_cross_check_no_issues(env_dir):
    ref = _write(env_dir / "ref.env", "X=1\n")
    tgt = _write(env_dir / "tgt.env", "X=hello\n")
    result = cross_check(ref, tgt)
    output = format_cross_check(result)
    assert "All keys present" in output


def test_format_cross_check_with_issues(env_dir):
    ref = _write(env_dir / "ref.env", "MISSING_KEY=val\n")
    tgt = _write(env_dir / "tgt.env", "OTHER=x\n")
    result = cross_check(ref, tgt)
    output = format_cross_check(result)
    assert "[MISSING]" in output


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_run_all_present(env_dir):
    ref = _write(env_dir / "ref.env", "DB=localhost\n")
    tgt = _write(env_dir / "tgt.env", "DB=prod\n")
    runner = CliRunner()
    result = runner.invoke(cross_check_cmd, ["run", str(ref), str(tgt)])
    assert result.exit_code == 0
    assert "All keys present" in result.output


def test_cli_run_strict_exits_nonzero_on_issues(env_dir):
    ref = _write(env_dir / "ref.env", "MISSING=val\n")
    tgt = _write(env_dir / "tgt.env", "OTHER=x\n")
    runner = CliRunner()
    result = runner.invoke(cross_check_cmd, ["run", str(ref), str(tgt), "--strict"])
    assert result.exit_code != 0
