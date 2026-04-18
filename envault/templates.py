"""Template management for envault — save and apply .env templates."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

DEFAULT_TEMPLATES_FILE = Path.home() / ".envault" / "templates.json"


def _load_templates(path: Path = DEFAULT_TEMPLATES_FILE) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_templates(data: dict, path: Path = DEFAULT_TEMPLATES_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def save_template(name: str, keys: list[str], description: str = "",
                  path: Path = DEFAULT_TEMPLATES_FILE) -> None:
    """Save a named template with a list of expected env keys."""
    data = _load_templates(path)
    if name in data:
        raise ValueError(f"Template '{name}' already exists.")
    data[name] = {"keys": keys, "description": description}
    _save_templates(data, path)


def remove_template(name: str, path: Path = DEFAULT_TEMPLATES_FILE) -> None:
    data = _load_templates(path)
    if name not in data:
        raise KeyError(f"Template '{name}' not found.")
    del data[name]
    _save_templates(data, path)


def get_template(name: str, path: Path = DEFAULT_TEMPLATES_FILE) -> dict:
    data = _load_templates(path)
    if name not in data:
        raise KeyError(f"Template '{name}' not found.")
    return data[name]


def list_templates(path: Path = DEFAULT_TEMPLATES_FILE) -> list[str]:
    return list(_load_templates(path).keys())


def check_env_against_template(env_content: str, template_name: str,
                                path: Path = DEFAULT_TEMPLATES_FILE) -> dict:
    """Return missing and extra keys compared to the template."""
    tmpl = get_template(template_name, path)
    expected = set(tmpl["keys"])
    present = {
        line.split("=", 1)[0].strip()
        for line in env_content.splitlines()
        if "=" in line and not line.startswith("#")
    }
    return {"missing": sorted(expected - present), "extra": sorted(present - expected)}
