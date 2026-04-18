import json
import pytest
from pathlib import Path
import envault.profiles as profiles_mod
from envault.profiles import add_profile, remove_profile, get_profile, list_profiles


@pytest.fixture(autouse=True)
def isolated_profiles(tmp_path, monkeypatch):
    profiles_file = tmp_path / ".envault_profiles.json"
    monkeypatch.setattr(profiles_mod, "PROFILES_FILE", profiles_file)
    yield profiles_file


def test_add_profile_creates_entry():
    profile = add_profile("dev", ".env.dev.vault", "Development environment")
    assert profile["vault_path"] == ".env.dev.vault"
    assert profile["description"] == "Development environment"


def test_add_profile_persists(isolated_profiles):
    add_profile("staging", ".env.staging.vault")
    data = json.loads(isolated_profiles.read_text())
    assert "staging" in data
    assert data["staging"]["vault_path"] == ".env.staging.vault"


def test_add_duplicate_profile_raises():
    add_profile("prod", ".env.prod.vault")
    with pytest.raises(ValueError, match="already exists"):
        add_profile("prod", ".env.prod.vault")


def test_get_profile_returns_correct_data():
    add_profile("dev", ".env.dev.vault", "Dev")
    profile = get_profile("dev")
    assert profile["vault_path"] == ".env.dev.vault"
    assert profile["description"] == "Dev"


def test_get_missing_profile_raises():
    with pytest.raises(KeyError, match="not found"):
        get_profile("nonexistent")


def test_remove_profile():
    add_profile("temp", ".env.temp.vault")
    remove_profile("temp")
    assert "temp" not in list_profiles()


def test_remove_missing_profile_raises():
    with pytest.raises(KeyError, match="not found"):
        remove_profile("ghost")


def test_list_profiles_empty_when_no_file():
    assert list_profiles() == {}


def test_list_profiles_returns_all():
    add_profile("dev", ".env.dev.vault")
    add_profile("prod", ".env.prod.vault")
    all_profiles = list_profiles()
    assert set(all_profiles.keys()) == {"dev", "prod"}
