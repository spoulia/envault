"""Tests for envault.env_diff_apply."""
import pytest
from pathlib import Path
from envault.env_diff_apply import apply_patch, ApplyResult


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text("HOST=localhost\nPORT=5432\nDEBUG=false\n")
    return f


def test_add_new_key(env_file: Path):
    result = apply_patch(env_file, add={"NEW_KEY": "hello"})
    assert "NEW_KEY" in result.added
    assert "NEW_KEY=hello" in env_file.read_text()


def test_add_existing_key_skipped(env_file: Path):
    result = apply_patch(env_file, add={"HOST": "newhost"})
    assert "HOST" in result.skipped
    assert "HOST=localhost" in env_file.read_text()


def test_update_existing_key(env_file: Path):
    result = apply_patch(env_file, update={"PORT": "9999"})
    assert "PORT" in result.updated
    assert "PORT=9999" in env_file.read_text()


def test_update_missing_key_adds_when_overwrite(env_file: Path):
    result = apply_patch(env_file, update={"MISSING": "val"}, overwrite=True)
    assert "MISSING" in result.added
    assert "MISSING=val" in env_file.read_text()


def test_update_missing_key_skipped_when_no_overwrite(env_file: Path):
    result = apply_patch(env_file, update={"MISSING": "val"}, overwrite=False)
    assert "MISSING" in result.skipped
    assert "MISSING" not in env_file.read_text()


def test_remove_existing_key(env_file: Path):
    result = apply_patch(env_file, remove=["DEBUG"])
    assert "DEBUG" in result.removed
    assert "DEBUG" not in env_file.read_text()


def test_remove_missing_key_skipped(env_file: Path):
    result = apply_patch(env_file, remove=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped


def test_combined_patch(env_file: Path):
    result = apply_patch(
        env_file,
        add={"NEW": "1"},
        update={"HOST": "remotehost"},
        remove=["DEBUG"],
    )
    text = env_file.read_text()
    assert "NEW" in result.added
    assert "HOST" in result.updated
    assert "DEBUG" in result.removed
    assert "NEW=1" in text
    assert "HOST=remotehost" in text
    assert "DEBUG" not in text


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        apply_patch(tmp_path / "ghost.env", add={"K": "v"})


def test_apply_result_is_dataclass(env_file: Path):
    result = apply_patch(env_file, add={"X": "y"})
    assert isinstance(result, ApplyResult)
