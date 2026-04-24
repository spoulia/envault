"""Tests for envault.env_sign."""
import json
from pathlib import Path

import pytest

from envault.env_sign import SignResult, VerifyResult, sign_file, verify_file

SECRET = "super-secret-key"


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=abc123\n")
    return p


def test_sign_returns_sign_result(env_file: Path) -> None:
    result = sign_file(env_file, SECRET)
    assert isinstance(result, SignResult)


def test_sign_creates_sig_file(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    sig = env_file.with_suffix(".sig")
    assert sig.exists()


def test_sig_file_is_valid_json(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    sig = env_file.with_suffix(".sig")
    data = json.loads(sig.read_text())
    assert "signature" in data
    assert data["algorithm"] == "sha256"
    assert data["version"] == 1


def test_sign_custom_output_path(env_file: Path, tmp_path: Path) -> None:
    custom = tmp_path / "custom.sig"
    sign_file(env_file, SECRET, sig_path=custom)
    assert custom.exists()


def test_sign_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        sign_file(tmp_path / "missing.env", SECRET)


def test_verify_valid_signature(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    result = verify_file(env_file, SECRET)
    assert isinstance(result, VerifyResult)
    assert result.valid is True
    assert result.reason == ""


def test_verify_wrong_secret_fails(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    result = verify_file(env_file, "wrong-secret")
    assert result.valid is False
    assert "mismatch" in result.reason


def test_verify_tampered_file_fails(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    env_file.write_text("DB_HOST=evil\n")
    result = verify_file(env_file, SECRET)
    assert result.valid is False


def test_verify_missing_sig_file(env_file: Path) -> None:
    result = verify_file(env_file, SECRET)
    assert result.valid is False
    assert "not found" in result.reason


def test_verify_missing_env_file(env_file: Path) -> None:
    sign_file(env_file, SECRET)
    env_file.unlink()
    result = verify_file(env_file, SECRET)
    assert result.valid is False
    assert "not found" in result.reason


def test_verify_corrupt_sig_file(env_file: Path) -> None:
    sig = env_file.with_suffix(".sig")
    sig.write_text("not-json{{{")
    result = verify_file(env_file, SECRET)
    assert result.valid is False
    assert "invalid signature file" in result.reason
