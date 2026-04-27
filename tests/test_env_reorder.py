"""Tests for envault.env_reorder."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_reorder import (
    ReorderResult,
    reorder_file,
    reordered_count,
    unmatched_count,
)
from envault.cli_env_reorder import reorder_cmd


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("ALPHA=1\nBETA=2\nGAMMA=3\nDELTA=4\n")
    return p


def test_reorder_returns_reorder_result_type(env_file: Path) -> None:
    result = reorder_file(env_file, order=["GAMMA", "ALPHA"])
    assert isinstance(result, ReorderResult)


def test_reorder_writes_keys_in_given_order(env_file: Path) -> None:
    reorder_file(env_file, order=["GAMMA", "ALPHA", "BETA", "DELTA"])
    lines = [ln for ln in env_file.read_text().splitlines() if ln.strip()]
    keys = [ln.split("=")[0] for ln in lines]
    assert keys == ["GAMMA", "ALPHA", "BETA", "DELTA"]


def test_reorder_ordered_keys_list(env_file: Path) -> None:
    result = reorder_file(env_file, order=["DELTA", "BETA"])
    assert result.ordered_keys == ["DELTA", "BETA"]


def test_reorder_unmatched_keys_appended_by_default(env_file: Path) -> None:
    result = reorder_file(env_file, order=["GAMMA"])
    assert set(result.unmatched_keys) == {"ALPHA", "BETA", "DELTA"}
    content = env_file.read_text()
    for key in ["ALPHA", "BETA", "DELTA"]:
        assert key in content


def test_reorder_drop_unmatched_removes_keys(env_file: Path) -> None:
    reorder_file(env_file, order=["GAMMA", "ALPHA"], append_unmatched=False)
    content = env_file.read_text()
    assert "BETA" not in content
    assert "DELTA" not in content


def test_reorder_output_to_separate_file(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.env"
    result = reorder_file(env_file, order=["BETA", "ALPHA"], output=out)
    assert out.exists()
    assert result.output == str(out)
    # source should be unchanged
    assert env_file.read_text().splitlines()[0] == "ALPHA=1"


def test_reorder_missing_order_key_not_in_ordered_list(env_file: Path) -> None:
    result = reorder_file(env_file, order=["NONEXISTENT", "ALPHA"])
    assert "NONEXISTENT" not in result.ordered_keys
    assert "ALPHA" in result.ordered_keys


def test_reordered_count_helper(env_file: Path) -> None:
    result = reorder_file(env_file, order=["ALPHA", "BETA"])
    assert reordered_count(result) == 2


def test_unmatched_count_helper(env_file: Path) -> None:
    result = reorder_file(env_file, order=["ALPHA"])
    assert unmatched_count(result) == 3


def test_reorder_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        reorder_file(tmp_path / "ghost.env", order=["KEY"])


def test_cli_run_reorders_and_reports(env_file: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        reorder_cmd,
        ["run", str(env_file), "-k", "DELTA", "-k", "GAMMA", "-k", "BETA", "-k", "ALPHA"],
    )
    assert result.exit_code == 0
    assert "Reordered 4 key(s)" in result.output


def test_cli_run_drop_unmatched_reports(env_file: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        reorder_cmd,
        ["run", str(env_file), "-k", "ALPHA", "--drop-unmatched"],
    )
    assert result.exit_code == 0
    assert "Dropped" in result.output
