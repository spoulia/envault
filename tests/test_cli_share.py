"""CLI-level tests for the share export/import commands."""

import json
from pathlib import Path
from click.testing import CliRunner
from envault.cli_share import share
from envault.vault import lock


SAMPLE_ENV = "API_KEY=abc123\nSECRET=xyz\n"
PASSWORD = "cli-test-pass"


def _setup_vault(tmp_path: Path) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), str(vault_file), PASSWORD)
    return vault_file


def test_export_creates_bundle_file(tmp_path: Path) -> None:
    vault_file = _setup_vault(tmp_path)
    bundle_file = tmp_path / "bundle.json"
    runner = CliRunner()
    result = runner.invoke(
        share,
        ["export", str(vault_file), "--password", PASSWORD, "--output", str(bundle_file)],
    )
    assert result.exit_code == 0, result.output
    assert bundle_file.exists()
    data = json.loads(bundle_file.read_text())
    assert "data" in data


def test_import_restores_vault(tmp_path: Path) -> None:
    vault_file = _setup_vault(tmp_path)
    bundle_file = tmp_path / "bundle.json"
    restored = tmp_path / "restored.vault"
    runner = CliRunner()
    runner.invoke(
        share,
        ["export", str(vault_file), "--password", PASSWORD, "--output", str(bundle_file)],
    )
    result = runner.invoke(
        share,
        ["import", str(bundle_file), "--password", PASSWORD, "--output", str(restored)],
    )
    assert result.exit_code == 0, result.output
    assert restored.read_bytes() == vault_file.read_bytes()


def test_export_missing_vault_shows_error(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        share,
        ["export", str(tmp_path / "ghost.vault"), "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_import_wrong_password_shows_error(tmp_path: Path) -> None:
    vault_file = _setup_vault(tmp_path)
    bundle_file = tmp_path / "bundle.json"
    runner = CliRunner()
    runner.invoke(
        share,
        ["export", str(vault_file), "--password", PASSWORD, "--output", str(bundle_file)],
    )
    result = runner.invoke(
        share,
        ["import", str(bundle_file), "--password", "bad-pass", "--output", str(tmp_path / "out.vault")],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
