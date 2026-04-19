"""Tests for envault.env_defaults."""
import pytest
from pathlib import Path

from envault.env_defaults import apply_defaults, DefaultsResult


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("EXISTING=hello\nKEPT=world\n")
    return p


def test_apply_defaults_adds_missing_key(env_file: Path):
    result = apply_defaults(env_file, {"NEW_KEY": "newval"})
    assert "NEW_KEY" in result.applied
    content = env_file.read_text()
    assert "NEW_KEY=newval" in content


def test_apply_defaults_skips_existing_key(env_file: Path):
    result = apply_defaults(env_file, {"EXISTING": "replaced"})
    assert "EXISTING" in result.skipped
    content = env_file.read_text()
    assert "EXISTING=hello" in content


def test_apply_defaults_overwrite_replaces_existing(env_file: Path):
    result = apply_defaults(env_file, {"EXISTING": "replaced"}, overwrite=True)
    assert "EXISTING" in result.applied
    content = env_file.read_text()
    assert "EXISTING=replaced" in content


def test_apply_defaults_returns_defaults_result_type(env_file: Path):
    result = apply_defaults(env_file, {"FOO": "bar"})
    assert isinstance(result, DefaultsResult)


def test_apply_defaults_counts_are_correct(env_file: Path):
    result = apply_defaults(env_file, {"EXISTING": "x", "BRAND_NEW": "y"})
    assert result.applied_count == 1
    assert result.skipped_count == 1


def test_apply_defaults_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        apply_defaults(tmp_path / "missing.env", {"K": "v"})


def test_apply_defaults_writes_to_output_path(env_file: Path, tmp_path: Path):
    out = tmp_path / "out.env"
    apply_defaults(env_file, {"Z": "99"}, output_path=out)
    assert out.exists()
    assert "Z=99" in out.read_text()
    # original unchanged
    assert "Z=99" not in env_file.read_text()


def test_apply_defaults_preserves_existing_keys(env_file: Path):
    apply_defaults(env_file, {"EXTRA": "val"})
    content = env_file.read_text()
    assert "KEPT=world" in content
    assert "EXISTING=hello" in content
