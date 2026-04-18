import pytest
from click.testing import CliRunner
from envault.cli_profiles import profiles
from envault import profiles as profiles_module


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_module, "PROFILES_FILE", tmp_path / "profiles.json")


@pytest.fixture
def runner():
    return CliRunner()


def test_add_profile_success(runner):
    result = runner.invoke(profiles, ["add", "dev", "/path/to/dev.vault"])
    assert result.exit_code == 0
    assert "Profile 'dev' added" in result.output


def test_add_profile_with_description(runner):
    result = runner.invoke(profiles, ["add", "prod", "/path/prod.vault", "-d", "Production"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_add_duplicate_profile_shows_error(runner):
    runner.invoke(profiles, ["add", "dev", "/path/dev.vault"])
    result = runner.invoke(profiles, ["add", "dev", "/other/path.vault"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remove_profile_success(runner):
    runner.invoke(profiles, ["add", "dev", "/path/dev.vault"])
    result = runner.invoke(profiles, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_profile_shows_error(runner):
    result = runner.invoke(profiles, ["remove", "nonexistent"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_show_profile(runner):
    runner.invoke(profiles, ["add", "staging", "/path/staging.vault", "-d", "Staging env"])
    result = runner.invoke(profiles, ["show", "staging"])
    assert result.exit_code == 0
    assert "/path/staging.vault" in result.output
    assert "Staging env" in result.output


def test_show_missing_profile_shows_error(runner):
    result = runner.invoke(profiles, ["show", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_list_profiles_empty(runner):
    result = runner.invoke(profiles, ["list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_list_profiles_shows_all(runner):
    runner.invoke(profiles, ["add", "dev", "/dev.vault"])
    runner.invoke(profiles, ["add", "prod", "/prod.vault", "-d", "Live"])
    result = runner.invoke(profiles, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output
    assert "Live" in result.output
