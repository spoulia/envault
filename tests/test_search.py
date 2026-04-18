"""Tests for envault.search."""
import pytest
from pathlib import Path
from envault.vault import lock
from envault.search import search_vault, search_many, SearchResult

ENV_CONTENT = """DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=supersecret
API_KEY=abc123
DEBUG=true
"""

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    env_file = tmp_path / ".env"
    env_file.write_text(ENV_CONTENT)
    lock(str(env_file), str(vf), PASSWORD)
    return vf


def test_search_finds_key_by_prefix(vault_file):
    results = search_vault(vault_file, PASSWORD, "^DB_")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "SECRET_KEY" not in keys


def test_search_returns_search_result_type(vault_file):
    results = search_vault(vault_file, PASSWORD, "DEBUG")
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].key == "DEBUG"


def test_search_values(vault_file):
    results = search_vault(vault_file, PASSWORD, "localhost", search_values=True)
    assert any(r.key == "DB_HOST" for r in results)


def test_search_values_off_by_default(vault_file):
    results = search_vault(vault_file, PASSWORD, "localhost", search_values=False)
    assert results == []


def test_search_ignore_case(vault_file):
    results = search_vault(vault_file, PASSWORD, "secret_key", ignore_case=True)
    assert any(r.key == "SECRET_KEY" for r in results)


def test_search_no_match(vault_file):
    results = search_vault(vault_file, PASSWORD, "NONEXISTENT")
    assert results == []


def test_search_wrong_password(vault_file):
    with pytest.raises(Exception):
        search_vault(vault_file, "wrongpass", "DB")


def test_search_missing_vault(tmp_path):
    with pytest.raises(FileNotFoundError):
        search_vault(tmp_path / "missing.vault", PASSWORD, "KEY")


def test_search_many_skips_missing(vault_file, tmp_path):
    missing = tmp_path / "ghost.vault"
    results = search_many([vault_file, missing], PASSWORD, "DB_")
    assert len(results) >= 2


def test_search_result_includes_line_number(vault_file):
    results = search_vault(vault_file, PASSWORD, "DB_HOST")
    assert results[0].line >= 1
