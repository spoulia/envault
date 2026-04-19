"""Tests for envault.env_chunk."""
import pytest
from pathlib import Path
from envault.env_chunk import chunk_file, ChunkResult, format_chunk


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    lines = [f"KEY_{i}=value_{i}" for i in range(25)]
    f.write_text("\n".join(lines))
    return f


def test_chunk_returns_chunk_result_type(env_file):
    result = chunk_file(env_file, chunk_size=10)
    assert isinstance(result, ChunkResult)


def test_chunk_correct_count(env_file):
    result = chunk_file(env_file, chunk_size=10)
    assert result.chunk_count == 3


def test_chunk_total_keys(env_file):
    result = chunk_file(env_file, chunk_size=10)
    assert result.total_keys == 25


def test_chunk_sizes(env_file):
    result = chunk_file(env_file, chunk_size=10)
    assert len(result.chunks[0]) == 10
    assert len(result.chunks[1]) == 10
    assert len(result.chunks[2]) == 5


def test_chunk_size_one(env_file):
    result = chunk_file(env_file, chunk_size=1)
    assert result.chunk_count == 25
    for chunk in result.chunks:
        assert len(chunk) == 1


def test_chunk_larger_than_file(env_file):
    result = chunk_file(env_file, chunk_size=100)
    assert result.chunk_count == 1
    assert len(result.chunks[0]) == 25


def test_chunk_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        chunk_file(tmp_path / "missing.env")


def test_chunk_invalid_size_raises(env_file):
    with pytest.raises(ValueError):
        chunk_file(env_file, chunk_size=0)


def test_chunk_empty_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("")
    result = chunk_file(f, chunk_size=5)
    assert result.total_keys == 0
    assert result.chunk_count == 1
    assert result.chunks[0] == {}


def test_format_chunk_contains_header(env_file):
    result = chunk_file(env_file, chunk_size=10)
    output = format_chunk(result.chunks[0], 0)
    assert "--- chunk 1 ---" in output


def test_format_chunk_contains_keys(env_file):
    result = chunk_file(env_file, chunk_size=10)
    output = format_chunk(result.chunks[0], 0)
    assert "KEY_0=value_0" in output
