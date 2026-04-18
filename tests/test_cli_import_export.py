"""Tests for envault.cli_import_export."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_import_export import impexp


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("API_KEY=secret\nHOST=localhost\n")
    return p


def test_export_json_stdout(runner, env_file):
    result = runner.invoke(impexp, ["export", str(env_file)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["API_KEY"] == "secret"


def test_export_csv_stdout(runner, env_file):
    result = runner.invoke(impexp, ["export", str(env_file), "--format", "csv"])
    assert result.exit_code == 0
    assert "key,value" in result.output
    assert "API_KEY" in result.output


def test_export_to_file(runner, env_file, tmp_path):
    out = tmp_path / "out.json"
    result = runner.invoke(impexp, ["export", str(env_file), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "HOST" in data


def test_import_json_creates_env(runner, tmp_path):
    src = tmp_path / "vars.json"
    src.write_text(json.dumps({"FOO": "bar"}))
    out = tmp_path / ".env"
    result = runner.invoke(impexp, ["import", str(src), str(out)])
    assert result.exit_code == 0
    assert "1 key(s)" in result.output
    assert "FOO=bar" in out.read_text()


def test_import_merge_flag(runner, tmp_path):
    existing = tmp_path / ".env"
    existing.write_text("OLD=yes\n")
    src = tmp_path / "new.json"
    src.write_text(json.dumps({"NEW": "val"}))
    result = runner.invoke(impexp, ["import", str(src), str(existing), "--merge"])
    assert result.exit_code == 0
    assert "Merged" in result.output
    text = existing.read_text()
    assert "OLD=yes" in text
    assert "NEW=val" in text


def test_import_bad_json_shows_error(runner, tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("not json")
    out = tmp_path / ".env"
    result = runner.invoke(impexp, ["import", str(src), str(out)])
    assert result.exit_code != 0
