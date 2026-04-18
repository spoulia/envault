"""Tests for envault.hooks and envault.cli_hooks."""
import json
import pytest
from click.testing import CliRunner
from envault.hooks import add_hook, remove_hook, get_hooks, run_hooks, HOOKS_FILE
from envault.cli_hooks import hooks


@pytest.fixture(autouse=True)
def isolated_hooks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield


def test_add_hook_creates_entry():
    add_hook("post-lock", "echo locked")
    assert "echo locked" in get_hooks("post-lock")


def test_add_hook_persists():
    add_hook("pre-unlock", "echo pre")
    data = json.loads(HOOKS_FILE.read_text())
    assert "echo pre" in data["pre-unlock"]


def test_add_duplicate_hook_raises():
    add_hook("post-lock", "echo locked")
    with pytest.raises(ValueError, match="already registered"):
        add_hook("post-lock", "echo locked")


def test_add_invalid_event_raises():
    with pytest.raises(ValueError, match="Invalid event"):
        add_hook("on-fire", "echo boom")


def test_remove_hook():
    add_hook("post-lock", "echo done")
    remove_hook("post-lock", "echo done")
    assert get_hooks("post-lock") == []


def test_remove_missing_hook_raises():
    with pytest.raises(KeyError):
        remove_hook("post-lock", "echo nothing")


def test_run_hooks_executes_commands():
    add_hook("post-unlock", "exit 0")
    results = run_hooks("post-unlock")
    assert results == [("exit 0", 0)]


def test_get_hooks_empty_when_no_file():
    assert get_hooks("pre-lock") == []


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_add_hook_success(runner):
    result = runner.invoke(hooks, ["add", "post-lock", "echo hi"])
    assert result.exit_code == 0
    assert "Hook added" in result.output


def test_cli_list_hooks(runner):
    add_hook("pre-lock", "echo before")
    result = runner.invoke(hooks, ["list", "pre-lock"])
    assert "echo before" in result.output


def test_cli_list_no_hooks(runner):
    result = runner.invoke(hooks, ["list"])
    assert "No hooks registered" in result.output


def test_cli_remove_hook_success(runner):
    add_hook("post-unlock", "echo bye")
    result = runner.invoke(hooks, ["remove", "post-unlock", "echo bye"])
    assert result.exit_code == 0
    assert "Hook removed" in result.output
