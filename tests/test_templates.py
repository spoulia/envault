import pytest
from pathlib import Path
from envault.templates import (
    save_template, remove_template, get_template,
    list_templates, check_env_against_template
)


@pytest.fixture
def isolated_templates(tmp_path):
    return tmp_path / "templates.json"


def test_save_template_creates_entry(isolated_templates):
    save_template("base", ["DB_URL", "SECRET_KEY"], path=isolated_templates)
    tmpl = get_template("base", path=isolated_templates)
    assert tmpl["keys"] == ["DB_URL", "SECRET_KEY"]


def test_save_template_persists(isolated_templates):
    save_template("base", ["A", "B"], path=isolated_templates)
    names = list_templates(path=isolated_templates)
    assert "base" in names


def test_save_duplicate_raises(isolated_templates):
    save_template("base", ["A"], path=isolated_templates)
    with pytest.raises(ValueError, match="already exists"):
        save_template("base", ["B"], path=isolated_templates)


def test_remove_template(isolated_templates):
    save_template("base", ["A"], path=isolated_templates)
    remove_template("base", path=isolated_templates)
    assert "base" not in list_templates(path=isolated_templates)


def test_remove_missing_raises(isolated_templates):
    with pytest.raises(KeyError):
        remove_template("ghost", path=isolated_templates)


def test_list_templates_empty(isolated_templates):
    assert list_templates(path=isolated_templates) == []


def test_check_env_no_diff(isolated_templates):
    save_template("web", ["PORT", "HOST"], path=isolated_templates)
    env = "PORT=8080\nHOST=localhost\n"
    result = check_env_against_template(env, "web", path=isolated_templates)
    assert result["missing"] == []
    assert result["extra"] == []


def test_check_env_missing_keys(isolated_templates):
    save_template("web", ["PORT", "HOST", "DEBUG"], path=isolated_templates)
    env = "PORT=8080\n"
    result = check_env_against_template(env, "web", path=isolated_templates)
    assert "HOST" in result["missing"]
    assert "DEBUG" in result["missing"]


def test_check_env_extra_keys(isolated_templates):
    save_template("minimal", ["PORT"], path=isolated_templates)
    env = "PORT=8080\nEXTRA=yes\n"
    result = check_env_against_template(env, "minimal", path=isolated_templates)
    assert "EXTRA" in result["extra"]
