"""Tests for envault.env_truncate."""
from pathlib import Path

import pytest

from envault.env_truncate import (
    TruncateResult,
    truncate_file,
    truncated_count,
    skipped_count,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "SHORT=hi\n"
        "LONG=" + "x" * 100 + "\n"
        "MEDIUM=" + "y" * 64 + "\n",
        encoding="utf-8",
    )
    return p


def test_truncate_returns_truncate_result_type(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=64, write=False)
    assert isinstance(result, TruncateResult)


def test_truncate_long_value_is_shortened(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=64, write=False)
    assert len(result.entries["LONG"]) <= 64


def test_truncate_short_value_unchanged(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=64, write=False)
    assert result.entries["SHORT"] == "hi"


def test_truncated_count(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=64, write=False)
    # LONG (100 chars) should be truncated; SHORT and MEDIUM (exactly 64) should not
    assert truncated_count(result) == 1
    assert "LONG" in result.truncated


def test_skipped_count(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=64, write=False)
    assert skipped_count(result) == 2
    assert "SHORT" in result.skipped
    assert "MEDIUM" in result.skipped


def test_truncate_suffix_appended(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=20, suffix="...", write=False)
    assert result.entries["LONG"].endswith("...")


def test_truncate_respects_max_length(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=20, suffix="...", write=False)
    assert len(result.entries["LONG"]) <= 20


def test_truncate_writes_file(env_file: Path) -> None:
    truncate_file(env_file, max_length=20, write=True)
    content = env_file.read_text(encoding="utf-8")
    assert len([v for v in content.splitlines() if v.startswith("LONG=")]) == 1
    long_val = next(l.partition("=")[2] for l in content.splitlines() if l.startswith("LONG="))
    assert len(long_val) <= 20


def test_truncate_specific_keys_only(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=10, keys=["SHORT"], write=False)
    # LONG is not in keys list, so it must remain untouched
    assert "LONG" not in result.truncated
    assert len(result.entries["LONG"]) == 100


def test_truncate_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        truncate_file(tmp_path / "missing.env", write=False)


def test_truncate_custom_suffix(env_file: Path) -> None:
    result = truncate_file(env_file, max_length=30, suffix="[cut]", write=False)
    assert result.entries["LONG"].endswith("[cut]")
