import pytest
from click.testing import CliRunner
from envault.cli_templates import templates
from envault.templates import save_template, DEFAULT_TEMPLATES_FILE
from pathlib import Path
import json


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    tfile = tmp_path / "templates.json"
    import envault.templates as tm
    monkeypatch.setattr(tm, "DEFAULT_TEMPLATES_FILE", tfile)
    import envault.cli_templates as ct
    monkeypatch.setattr(ct, "DEFAULT_TEMPLATES_FILE", tfile)
    return tfile


@pytest.fixture
def runner():
    return CliRunner()


def test_add_template_success(isolated, runner):
    result = runner.invoke(templates, ["add", "prod", "DB_URL", "SECRET"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_add_template_with_description(isolated, runner):
    result = runner.invoke(templates, ["add", "prod", "DB_URL", "--description", "Production env"])
    assert result.exit_code == 0


def test_add_duplicate_shows_error(isolated, runner):
    runner.invoke(templates, ["add", "prod", "DB_URL"])
    result = runner.invoke(templates, ["add", "prod", "OTHER"])
    assert "Error" in result.output


def test_list_shows_templates(isolated, runner):
    runner.invoke(templates, ["add", "alpha", "A"])
    runner.invoke(templates, ["add", "beta", "B"])
    result = runner.invoke(templates, ["list"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_show_template(isolated, runner):
    runner.invoke(templates, ["add", "prod", "DB_URL", "SECRET", "--description", "Prod"])
    result = runner.invoke(templates, ["show", "prod"])
    assert "DB_URL" in result.output
    assert "Prod" in result.output


def test_remove_template_success(isolated, runner):
    runner.invoke(templates, ["add", "old", "X"])
    result = runner.invoke(templates, ["remove", "old"])
    assert "removed" in result.output


def test_check_template_match(isolated, runner, tmp_path):
    runner.invoke(templates, ["add", "web", "PORT", "HOST"])
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nHOST=localhost\n")
    result = runner.invoke(templates, ["check", "web", str(env_file)])
    assert "match" in result.output


def test_check_template_missing(isolated, runner, tmp_path):
    runner.invoke(templates, ["add", "web", "PORT", "HOST", "DEBUG"])
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\n")
    result = runner.invoke(templates, ["check", "web", str(env_file)])
    assert "Missing" in result.output
