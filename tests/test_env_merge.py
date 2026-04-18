import pytest
from pathlib import Path
from envault.env_merge import merge_files, write_merged, MergeResult


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_merge_no_conflicts(env_dir):
    a = _write(env_dir / "a.env", "FOO=1\nBAR=2\n")
    b = _write(env_dir / "b.env", "BAZ=3\n")
    result = merge_files([a, b])
    assert result.merged == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert result.conflicts == []


def test_merge_last_strategy_wins(env_dir):
    a = _write(env_dir / "a.env", "FOO=first\n")
    b = _write(env_dir / "b.env", "FOO=last\n")
    result = merge_files([a, b], strategy="last")
    assert result.merged["FOO"] == "last"
    assert len(result.conflicts) == 1
    assert result.conflicts[0][0] == "FOO"


def test_merge_first_strategy_wins(env_dir):
    a = _write(env_dir / "a.env", "FOO=first\n")
    b = _write(env_dir / "b.env", "FOO=last\n")
    result = merge_files([a, b], strategy="first")
    assert result.merged["FOO"] == "first"


def test_merge_error_strategy_raises(env_dir):
    a = _write(env_dir / "a.env", "FOO=1\n")
    b = _write(env_dir / "b.env", "FOO=2\n")
    with pytest.raises(ValueError, match="Conflict on key 'FOO'"):
        merge_files([a, b], strategy="error")


def test_merge_identical_values_no_conflict(env_dir):
    a = _write(env_dir / "a.env", "FOO=same\n")
    b = _write(env_dir / "b.env", "FOO=same\n")
    result = merge_files([a, b])
    assert result.conflicts == []
    assert result.merged["FOO"] == "same"


def test_merge_missing_file_raises(env_dir):
    with pytest.raises(FileNotFoundError):
        merge_files([env_dir / "nonexistent.env"])


def test_merge_sources_recorded(env_dir):
    a = _write(env_dir / "a.env", "X=1\n")
    b = _write(env_dir / "b.env", "Y=2\n")
    result = merge_files([a, b])
    assert str(a) in result.sources
    assert str(b) in result.sources


def test_write_merged_creates_file(env_dir):
    a = _write(env_dir / "a.env", "FOO=1\nBAR=2\n")
    result = merge_files([a])
    dest = env_dir / "merged.env"
    write_merged(result, dest)
    assert dest.exists()
    content = dest.read_text()
    assert "FOO=1" in content
    assert "BAR=2" in content
