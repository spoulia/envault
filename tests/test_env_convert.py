"""Tests for envault.env_convert."""
import json
import pytest
from pathlib import Path
from envault.env_convert import convert_env, ConvertResult


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env"
    f.write_text('DB_HOST=localhost\nDB_PORT=5432\nSECRET="my secret"\n')
    return f


def test_convert_to_json(env_file, tmp_path):
    out = tmp_path / "out.json"
    result = convert_env(env_file, out, "json")
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"
    assert data["SECRET"] == "my secret"


def test_convert_returns_convert_result(env_file, tmp_path):
    out = tmp_path / "out.json"
    result = convert_env(env_file, out, "json")
    assert isinstance(result, ConvertResult)
    assert result.target_format == "json"
    assert result.keys_converted == 3


def test_convert_to_dotenv(env_file, tmp_path):
    out = tmp_path / "out.env"
    convert_env(env_file, out, "dotenv")
    text = out.read_text()
    assert "DB_HOST=localhost" in text


def test_convert_to_yaml(env_file, tmp_path):
    out = tmp_path / "out.yaml"
    convert_env(env_file, out, "yaml")
    text = out.read_text()
    assert "DB_HOST: localhost" in text


def test_convert_to_toml(env_file, tmp_path):
    out = tmp_path / "out.toml"
    convert_env(env_file, out, "toml")
    text = out.read_text()
    assert 'DB_HOST = "localhost"' in text


def test_convert_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        convert_env(tmp_path / "ghost.env", tmp_path / "out.json", "json")


def test_convert_unsupported_format_raises(env_file, tmp_path):
    with pytest.raises(ValueError, match="Unsupported format"):
        convert_env(env_file, tmp_path / "out.xml", "xml")  # type: ignore


def test_convert_output_path_in_result(env_file, tmp_path):
    out = tmp_path / "result.json"
    result = convert_env(env_file, out, "json")
    assert result.output_path == str(out)
