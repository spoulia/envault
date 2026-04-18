"""Tests for envault.import_export."""
import json
import pytest
from pathlib import Path
from envault.import_export import export_env, import_env


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=abc123\nDB_URL=postgres://localhost/db\nDEBUG=true\n")
    return p


def test_export_json_returns_dict(env_file):
    result = export_env(env_file, "json")
    data = json.loads(result)
    assert data["API_KEY"] == "abc123"
    assert data["DB_URL"] == "postgres://localhost/db"


def test_export_csv_has_header(env_file):
    result = export_env(env_file, "csv")
    lines = result.strip().splitlines()
    assert lines[0] == "key,value"
    assert any("API_KEY" in l for l in lines)


def test_export_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_env(tmp_path / "missing.env", "json")


def test_import_json_creates_env(tmp_path):
    out = tmp_path / ".env"
    content = json.dumps({"FOO": "bar", "BAZ": "qux"})
    count = import_env(out, content, "json")
    assert count == 2
    text = out.read_text()
    assert "FOO=bar" in text
    assert "BAZ=qux" in text


def test_import_csv_creates_env(tmp_path):
    out = tmp_path / ".env"
    content = "key,value\nHOST,localhost\nPORT,5432\n"
    count = import_env(out, content, "csv")
    assert count == 2
    text = out.read_text()
    assert "HOST=localhost" in text


def test_import_merge_preserves_existing(tmp_path):
    out = tmp_path / ".env"
    out.write_text("EXISTING=yes\nFOO=old\n")
    content = json.dumps({"FOO": "new", "BAR": "added"})
    count = import_env(out, content, "json", merge=True)
    assert count == 3
    text = out.read_text()
    assert "EXISTING=yes" in text
    assert "FOO=new" in text
    assert "BAR=added" in text


def test_import_invalid_json_raises(tmp_path):
    with pytest.raises((ValueError, json.JSONDecodeError)):
        import_env(tmp_path / ".env", "not json", "json")


def test_import_csv_missing_key_column_raises(tmp_path):
    with pytest.raises(ValueError, match="CSV must have"):
        import_env(tmp_path / ".env", "name,val\na,b\n", "csv")
