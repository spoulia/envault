"""Tests for envault.env_diff_summary."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.env_diff_summary import DiffSummaryResult, format_summary, summarise
from envault.cli_env_diff_summary import diff_summary_cmd


@pytest.fixture()
def env_pair(tmp_path: Path):
    before = tmp_path / "before.env"
    after = tmp_path / "after.env"
    before.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nSECRET=old_secret\nDEPRECATED=yes\n"
    )
    after.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nSECRET=new_secret\nNEW_KEY=hello\n"
    )
    return before, after


def test_summarise_returns_diff_summary_result(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert isinstance(result, DiffSummaryResult)


def test_detects_added_key(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert "NEW_KEY" in result.added
    assert result.added["NEW_KEY"] == "hello"


def test_detects_removed_key(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert "DEPRECATED" in result.removed


def test_detects_changed_key(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert "SECRET" in result.changed
    old_v, new_v = result.changed["SECRET"]
    assert old_v == "old_secret"
    assert new_v == "new_secret"


def test_unchanged_keys_not_in_changes(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert "DB_HOST" not in result.added
    assert "DB_HOST" not in result.removed
    assert "DB_HOST" not in result.changed
    assert "DB_HOST" in result.unchanged


def test_has_changes_true_when_differences(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    assert result.has_changes is True


def test_has_changes_false_when_identical(tmp_path: Path):
    f = tmp_path / "a.env"
    f.write_text("KEY=value\n")
    result = summarise(f, f)
    assert result.has_changes is False


def test_format_summary_masks_values_by_default(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    output = format_summary(result)
    assert "old_secret" not in output
    assert "new_secret" not in output
    assert "***" in output


def test_format_summary_shows_values_when_unmasked(env_pair):
    before, after = env_pair
    result = summarise(before, after)
    output = format_summary(result, mask_values=False)
    assert "new_secret" in output


def test_format_summary_no_changes_message(tmp_path: Path):
    f = tmp_path / "same.env"
    f.write_text("KEY=value\n")
    result = summarise(f, f)
    assert format_summary(result) == "No changes detected."


def test_missing_before_raises(tmp_path: Path):
    after = tmp_path / "after.env"
    after.write_text("KEY=val\n")
    with pytest.raises(FileNotFoundError):
        summarise(tmp_path / "ghost.env", after)


# --- CLI tests ---


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_show_outputs_summary(runner, env_pair):
    before, after = env_pair
    res = runner.invoke(diff_summary_cmd, ["show", str(before), str(after)])
    assert res.exit_code == 0
    assert "Added" in res.output or "Changed" in res.output


def test_cli_counts_only_flag(runner, env_pair):
    before, after = env_pair
    res = runner.invoke(
        diff_summary_cmd, ["show", "--counts-only", str(before), str(after)]
    )
    assert res.exit_code == 0
    assert "added=" in res.output
    assert "removed=" in res.output
    assert "changed=" in res.output


def test_cli_no_mask_shows_values(runner, env_pair):
    before, after = env_pair
    res = runner.invoke(
        diff_summary_cmd, ["show", "--no-mask", str(before), str(after)]
    )
    assert res.exit_code == 0
    assert "new_secret" in res.output
