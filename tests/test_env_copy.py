"""Tests for envault.env_copy."""
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.vault import lock
from envault.env_copy import copy_keys, CopyResult
from envault.cli_env_copy import copy


PASSWORD = "secret"
SRC_ENV = "API_KEY=abc123\nDB_URL=postgres://localhost/db\nDEBUG=true\n"
DST_ENV = "APP_NAME=myapp\nAPI_KEY=old\n"


@pytest.fixture()
def src_vault(tmp_path):
    p = tmp_path / "src.vault"
    lock(p, SRC_ENV, PASSWORD)
    return p


@pytest.fixture()
def dst_vault(tmp_path):
    p = tmp_path / "dst.vault"
    lock(p, DST_ENV, PASSWORD)
    return p


def test_copy_all_keys(src_vault, tmp_path):
    dst = tmp_path / "new.vault"
    result = copy_keys(src_vault, PASSWORD, dst, PASSWORD)
    assert isinstance(result, CopyResult)
    assert set(result.copied) == {"API_KEY", "DB_URL", "DEBUG"}
    assert result.skipped == []


def test_copy_specific_keys(src_vault, tmp_path):
    dst = tmp_path / "new.vault"
    result = copy_keys(src_vault, PASSWORD, dst, PASSWORD, keys=["API_KEY", "DEBUG"])
    assert result.copied == ["API_KEY", "DEBUG"]
    assert result.skipped == []


def test_copy_skips_existing_without_overwrite(src_vault, dst_vault):
    result = copy_keys(src_vault, PASSWORD, dst_vault, PASSWORD, keys=["API_KEY"])
    assert "API_KEY" in result.skipped
    assert result.copied == []


def test_copy_overwrites_when_flag_set(src_vault, dst_vault):
    result = copy_keys(src_vault, PASSWORD, dst_vault, PASSWORD, keys=["API_KEY"], overwrite=True)
    assert "API_KEY" in result.copied


def test_copy_skips_missing_key(src_vault, tmp_path):
    dst = tmp_path / "new.vault"
    result = copy_keys(src_vault, PASSWORD, dst, PASSWORD, keys=["NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped
    assert result.copied == []


def test_copy_wrong_password_raises(src_vault, tmp_path):
    dst = tmp_path / "new.vault"
    with pytest.raises(Exception):
        copy_keys(src_vault, "wrong", dst, PASSWORD)


def test_cli_copy_run(src_vault, tmp_path):
    dst = tmp_path / "out.vault"
    runner = CliRunner()
    result = runner.invoke(
        copy,
        ["run", str(src_vault), str(dst),
         "--src-password", PASSWORD,
         "--dst-password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Copied" in result.output


def test_cli_copy_shows_skipped(src_vault, dst_vault):
    runner = CliRunner()
    result = runner.invoke(
        copy,
        ["run", str(src_vault), str(dst_vault),
         "--src-password", PASSWORD,
         "--dst-password", PASSWORD,
         "--key", "API_KEY"],
    )
    assert result.exit_code == 0
    assert "Skipped" in result.output
