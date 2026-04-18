"""Tag management for vault entries."""
import json
from pathlib import Path

TAGS_FILE = Path(".envault_tags.json")


def _load_tags() -> dict:
    if not TAGS_FILE.exists():
        return {}
    return json.loads(TAGS_FILE.read_text())


def _save_tags(data: dict) -> None:
    TAGS_FILE.write_text(json.dumps(data, indent=2))


def add_tag(vault_path: str, tag: str) -> None:
    data = _load_tags()
    tags = data.get(vault_path, [])
    if tag in tags:
        raise ValueError(f"Tag '{tag}' already exists on '{vault_path}'")
    tags.append(tag)
    data[vault_path] = tags
    _save_tags(data)


def remove_tag(vault_path: str, tag: str) -> None:
    data = _load_tags()
    tags = data.get(vault_path, [])
    if tag not in tags:
        raise KeyError(f"Tag '{tag}' not found on '{vault_path}'")
    tags.remove(tag)
    data[vault_path] = tags
    _save_tags(data)


def get_tags(vault_path: str) -> list:
    return _load_tags().get(vault_path, [])


def list_tagged(tag: str) -> list:
    data = _load_tags()
    return [path for path, tags in data.items() if tag in tags]


def clear_tags(vault_path: str) -> None:
    data = _load_tags()
    data.pop(vault_path, None)
    _save_tags(data)


def rename_tag(old_tag: str, new_tag: str) -> int:
    """Rename a tag across all vault entries.

    Returns the number of entries updated.
    """
    data = _load_tags()
    updated = 0
    for vault_path, tags in data.items():
        if old_tag in tags:
            tags[tags.index(old_tag)] = new_tag
            updated += 1
    if updated:
        _save_tags(data)
    return updated
