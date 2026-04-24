"""Tests for envault.env_interpolate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_interpolate import (
    InterpolateResult,
    format_interpolate,
    has_unresolved,
    interpolate_file,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "BASE_URL=https://example.com\n"
        "API_URL=${BASE_URL}/api\n"
        "FULL_URL=$API_URL/v1\n"
        "SECRET=abc123\n"
    )
    return p


def test_interpolate_returns_result_type(env_file: Path) -> None:
    result = interpolate_file(env_file)
    assert isinstance(result, InterpolateResult)


def test_simple_reference_resolved(env_file: Path) -> None:
    result = interpolate_file(env_file)
    assert result.resolved["API_URL"] == "https://example.com/api"


def test_chained_reference_resolved(env_file: Path) -> None:
    result = interpolate_file(env_file)
    # FULL_URL references API_URL which was already resolved in context
    assert "api" in result.resolved["FULL_URL"]


def test_plain_key_unchanged(env_file: Path) -> None:
    result = interpolate_file(env_file)
    assert result.resolved["SECRET"] == "abc123"


def test_unresolved_reference_reported(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("URL=${MISSING_VAR}/path\n")
    result = interpolate_file(p)
    assert "MISSING_VAR" in result.unresolved


def test_has_unresolved_true_when_missing(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("X=${GHOST}\n")
    result = interpolate_file(p)
    assert has_unresolved(result) is True


def test_has_unresolved_false_when_all_resolved(env_file: Path) -> None:
    result = interpolate_file(env_file)
    assert has_unresolved(result) is False


def test_extra_context_resolves_external_var(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("GREETING=Hello ${NAME}\n")
    result = interpolate_file(p, extra_context={"NAME": "World"})
    assert result.resolved["GREETING"] == "Hello World"
    assert result.unresolved == []


def test_original_dict_preserved(env_file: Path) -> None:
    result = interpolate_file(env_file)
    assert result.original["API_URL"] == "${BASE_URL}/api"


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        interpolate_file(tmp_path / "nonexistent.env")


def test_format_interpolate_produces_env_lines(env_file: Path) -> None:
    result = interpolate_file(env_file)
    output = format_interpolate(result)
    assert "API_URL=" in output
    assert "BASE_URL=https://example.com" in output
