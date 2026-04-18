"""Tests for envault/tags.py"""
import pytest
from pathlib import Path
from envault import tags as tags_module


@pytest.fixture(autouse=True)
def isolated_tags(tmp_path, monkeypatch):
    monkeypatch.setattr(tags_module, "TAGS_FILE", tmp_path / ".envault_tags.json")


def test_add_tag_creates_entry():
    tags_module.add_tag("dev.vault", "development")
    assert "development" in tags_module.get_tags("dev.vault")


def test_add_tag_persists():
    tags_module.add_tag("dev.vault", "ci")
    assert "ci" in tags_module.get_tags("dev.vault")


def test_add_duplicate_tag_raises():
    tags_module.add_tag("dev.vault", "staging")
    with pytest.raises(ValueError, match="already exists"):
        tags_module.add_tag("dev.vault", "staging")


def test_remove_tag():
    tags_module.add_tag("dev.vault", "remove-me")
    tags_module.remove_tag("dev.vault", "remove-me")
    assert "remove-me" not in tags_module.get_tags("dev.vault")


def test_remove_missing_tag_raises():
    with pytest.raises(KeyError):
        tags_module.remove_tag("dev.vault", "ghost")


def test_get_tags_empty_when_no_file():
    assert tags_module.get_tags("nonexistent.vault") == []


def test_list_tagged_returns_correct_vaults():
    tags_module.add_tag("a.vault", "prod")
    tags_module.add_tag("b.vault", "prod")
    tags_module.add_tag("c.vault", "dev")
    result = tags_module.list_tagged("prod")
    assert "a.vault" in result
    assert "b.vault" in result
    assert "c.vault" not in result


def test_clear_tags_removes_all():
    tags_module.add_tag("dev.vault", "x")
    tags_module.add_tag("dev.vault", "y")
    tags_module.clear_tags("dev.vault")
    assert tags_module.get_tags("dev.vault") == []
