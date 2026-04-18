"""Profile management: named sets of vault configurations (e.g. dev, staging, prod)."""
import json
import os
from pathlib import Path

PROFILES_FILE = Path(".envault_profiles.json")


def _load_profiles() -> dict:
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)


def _save_profiles(profiles: dict) -> None:
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def add_profile(name: str, vault_path: str, description: str = "") -> dict:
    """Register a named profile pointing to a vault file."""
    profiles = _load_profiles()
    if name in profiles:
        raise ValueError(f"Profile '{name}' already exists.")
    profiles[name] = {"vault_path": vault_path, "description": description}
    _save_profiles(profiles)
    return profiles[name]


def remove_profile(name: str) -> None:
    """Remove a named profile."""
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    del profiles[name]
    _save_profiles(profiles)


def get_profile(name: str) -> dict:
    """Retrieve a profile by name."""
    profiles = _load_profiles()
    if name not in profiles:
        raise KeyError(f"Profile '{name}' not found.")
    return profiles[name]


def list_profiles() -> dict:
    """Return all registered profiles."""
    return _load_profiles()
