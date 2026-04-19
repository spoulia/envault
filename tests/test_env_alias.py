"""Tests for envault.env_alias."""
import pytest
from pathlib import Path
from envault.env_alias import add_alias, remove_alias, list_aliases, resolve_aliases, AliasResult


@pytest.fixture
def alias_file(tmp_path):
    return tmp_path / "aliases.json"


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=hunter2\n")
    return f


def test_add_alias_creates_entry(alias_file):
    add_alias("database_host", "DB_HOST", alias_file)
    aliases = list_aliases(alias_file)
    assert "database_host" in aliases
    assert aliases["database_host"] == "DB_HOST"


def test_add_alias_persists(alias_file):
    add_alias("port", "DB_PORT", alias_file)
    aliases = list_aliases(alias_file)
    assert aliases["port"] == "DB_PORT"


def test_add_duplicate_alias_raises(alias_file):
    add_alias("host", "DB_HOST", alias_file)
    with pytest.raises(ValueError, match="already exists"):
        add_alias("host", "DB_HOST", alias_file)


def test_remove_alias(alias_file):
    add_alias("host", "DB_HOST", alias_file)
    remove_alias("host", alias_file)
    assert "host" not in list_aliases(alias_file)


def test_remove_missing_alias_raises(alias_file):
    with pytest.raises(KeyError):
        remove_alias("nonexistent", alias_file)


def test_list_aliases_empty_when_no_file(alias_file):
    assert list_aliases(alias_file) == {}


def test_resolve_aliases_returns_values(alias_file, env_file):
    add_alias("host", "DB_HOST", alias_file)
    add_alias("port", "DB_PORT", alias_file)
    results = resolve_aliases(env_file, alias_file)
    by_alias = {r.alias: r for r in results}
    assert by_alias["host"].resolved_value == "localhost"
    assert by_alias["port"].resolved_value == "5432"


def test_resolve_alias_returns_alias_result_type(alias_file, env_file):
    add_alias("secret", "SECRET", alias_file)
    results = resolve_aliases(env_file, alias_file)
    assert all(isinstance(r, AliasResult) for r in results)


def test_resolve_alias_missing_key_returns_none(alias_file, env_file):
    add_alias("ghost", "NONEXISTENT_KEY", alias_file)
    results = resolve_aliases(env_file, alias_file)
    ghost = next(r for r in results if r.alias == "ghost")
    assert ghost.resolved_value is None
