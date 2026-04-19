"""Tests for envault.env_mask."""
import pytest
from pathlib import Path
from envault.env_mask import mask_env, MaskResult, _is_sensitive, _mask_value


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "APP_NAME=myapp\n"
        "DB_PASSWORD=supersecret\n"
        "API_KEY=abc123\n"
        "DEBUG=true\n"
        "SECRET_TOKEN=tok_xyz\n"
    )
    return p


def test_mask_returns_mask_result_type(env_file):
    result = mask_env(env_file)
    assert isinstance(result, MaskResult)


def test_mask_hides_sensitive_values(env_file):
    result = mask_env(env_file)
    assert result.masked["DB_PASSWORD"] == "*" * len("supersecret")
    assert result.masked["API_KEY"] == "*" * len("abc123")
    assert result.masked["SECRET_TOKEN"] == "*" * len("tok_xyz")


def test_mask_preserves_non_sensitive(env_file):
    result = mask_env(env_file)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_masked_keys_list(env_file):
    result = mask_env(env_file)
    assert "DB_PASSWORD" in result.masked_keys
    assert "API_KEY" in result.masked_keys
    assert "APP_NAME" not in result.masked_keys


def test_total_count(env_file):
    result = mask_env(env_file)
    assert result.total == 5


def test_reveal_chars(env_file):
    result = mask_env(env_file, reveal_chars=2)
    assert result.masked["DB_PASSWORD"].startswith("su")
    assert "*" in result.masked["DB_PASSWORD"]


def test_extra_keys(env_file):
    result = mask_env(env_file, extra_keys=["APP_NAME"])
    assert result.masked["APP_NAME"] == "*" * len("myapp")


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        mask_env(tmp_path / "missing.env")


def test_is_sensitive_detects_patterns():
    assert _is_sensitive("DB_PASSWORD")
    assert _is_sensitive("API_KEY")
    assert not _is_sensitive("APP_NAME")


def test_mask_value_full():
    assert _mask_value("hello") == "*****"


def test_mask_value_reveal():
    assert _mask_value("hello", reveal_chars=2) == "he***"
