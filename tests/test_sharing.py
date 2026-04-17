"""Tests for the sharing module (export/import bundle round-trip)."""

import json
import pytest
from pathlib import Path
from envault.sharing import export_bundle, import_bundle, BUNDLE_VERSION
from envault.vault import lock


SAMPLE_ENV = "DB_HOST=localhost\nDB_PASS=secret\n"
PASSWORD = "team-password-123"


@pytest.fixture()
def locked_vault(tmp_path: Path) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(SAMPLE_ENV)
    vault_file = tmp_path / ".env.vault"
    lock(str(env_file), str(vault_file), PASSWORD)
    return vault_file


def test_export_bundle_returns_valid_json(locked_vault: Path) -> None:
    bundle_json = export_bundle(str(locked_vault), PASSWORD)
    bundle = json.loads(bundle_json)
    assert bundle["version"] == BUNDLE_VERSION
    assert "data" in bundle


def test_export_bundle_includes_recipient(locked_vault: Path) -> None:
    bundle_json = export_bundle(str(locked_vault), PASSWORD, recipient_hint="alice@example.com")
    bundle = json.loads(bundle_json)
    assert bundle["recipient"] == "alice@example.com"


def test_export_import_roundtrip(locked_vault: Path, tmp_path: Path) -> None:
    bundle_json = export_bundle(str(locked_vault), PASSWORD)
    output = tmp_path / "restored.vault"
    import_bundle(bundle_json, PASSWORD, str(output))
    assert output.exists()
    assert output.read_bytes() == locked_vault.read_bytes()


def test_import_wrong_password_raises(locked_vault: Path, tmp_path: Path) -> None:
    bundle_json = export_bundle(str(locked_vault), PASSWORD)
    with pytest.raises(Exception):
        import_bundle(bundle_json, "wrong-password", str(tmp_path / "out.vault"))


def test_export_missing_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        export_bundle(str(tmp_path / "nonexistent.vault"), PASSWORD)


def test_import_invalid_json_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid bundle format"):
        import_bundle("not-json", PASSWORD, str(tmp_path / "out.vault"))


def test_import_wrong_version_raises(locked_vault: Path, tmp_path: Path) -> None:
    bundle_json = export_bundle(str(locked_vault), PASSWORD)
    bundle = json.loads(bundle_json)
    bundle["version"] = 99
    with pytest.raises(ValueError, match="Unsupported bundle version"):
        import_bundle(json.dumps(bundle), PASSWORD, str(tmp_path / "out.vault"))
