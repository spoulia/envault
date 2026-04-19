"""Tests for envault.env_placeholder."""
import pytest
from pathlib import Path
from envault.env_placeholder import scan_placeholders, resolve_placeholders, PlaceholderResult


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "API_KEY=CHANGE_ME\n"
        "DB_URL=postgres://localhost/db\n"
        "SECRET=<your-secret>\n"
        "TOKEN=xxx\n"
        "PORT=5432\n"
    )
    return p


def test_scan_finds_placeholders(env_file):
    result = scan_placeholders(env_file)
    keys = [i.key for i in result.issues]
    assert "API_KEY" in keys
    assert "SECRET" in keys
    assert "TOKEN" in keys


def test_scan_ignores_real_values(env_file):
    result = scan_placeholders(env_file)
    keys = [i.key for i in result.issues]
    assert "DB_URL" not in keys
    assert "PORT" not in keys


def test_scan_returns_placeholder_result_type(env_file):
    result = scan_placeholders(env_file)
    assert isinstance(result, PlaceholderResult)


def test_has_issues_true_when_placeholders_present(env_file):
    result = scan_placeholders(env_file)
    assert result.has_issues is True


def test_has_issues_false_when_clean(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY=realvalue\nOTHER=also_real\n")
    result = scan_placeholders(p)
    assert result.has_issues is False


def test_resolve_replaces_placeholder(env_file):
    resolve_placeholders(env_file, {"API_KEY": "sk-abc123"})
    text = env_file.read_text()
    assert "API_KEY=sk-abc123" in text


def test_resolve_does_not_touch_real_values(env_file):
    resolve_placeholders(env_file, {"DB_URL": "other"})
    text = env_file.read_text()
    assert "DB_URL=postgres://localhost/db" in text


def test_resolve_returns_resolved_keys(env_file):
    result = resolve_placeholders(env_file, {"API_KEY": "sk-abc123", "TOKEN": "real-token"})
    assert "API_KEY" in result.resolved
    assert "TOKEN" in result.resolved


def test_resolve_overwrite_flag(env_file):
    result = resolve_placeholders(env_file, {"DB_URL": "new-url"}, overwrite=True)
    assert "DB_URL" in result.resolved
    assert "DB_URL=new-url" in env_file.read_text()


def test_scan_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        scan_placeholders(tmp_path / "missing.env")


def test_resolve_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_placeholders(tmp_path / "missing.env", {})
