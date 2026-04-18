"""Tests for envault.env_inject."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from envault.vault import lock
from envault.env_inject import inject_run


@pytest.fixture()
def vault_file(tmp_path: Path) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text("INJECT_KEY=hello\nSECRET_VAL=world\n")
    vault = tmp_path / ".env.vault"
    lock(env_file, vault, "pass123")
    return vault


def _py_print_env(var: str) -> list[str]:
    return [sys.executable, "-c", f"import os; print(os.environ.get('{var}', '__missing__'))"]


def test_inject_run_sets_variables(vault_file: Path):
    result = inject_run(vault_file, "pass123", _py_print_env("INJECT_KEY"))
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"


def test_inject_run_all_vars_available(vault_file: Path):
    result = inject_run(vault_file, "pass123", _py_print_env("SECRET_VAL"))
    assert result.stdout.strip() == "world"


def test_inject_missing_var_returns_missing(vault_file: Path):
    result = inject_run(vault_file, "pass123", _py_print_env("NO_SUCH_VAR"))
    assert result.stdout.strip() == "__missing__"


def test_inject_wrong_password_raises(vault_file: Path):
    with pytest.raises(Exception):
        inject_run(vault_file, "wrongpass", _py_print_env("INJECT_KEY"))


def test_inject_override_true_overwrites(vault_file: Path, monkeypatch):
    monkeypatch.setenv("INJECT_KEY", "original")
    result = inject_run(vault_file, "pass123", _py_print_env("INJECT_KEY"), override=True)
    assert result.stdout.strip() == "hello"


def test_inject_override_false_preserves_existing(vault_file: Path, monkeypatch):
    monkeypatch.setenv("INJECT_KEY", "original")
    result = inject_run(vault_file, "pass123", _py_print_env("INJECT_KEY"), override=False)
    assert result.stdout.strip() == "original"


def test_inject_extra_env_is_available(vault_file: Path):
    result = inject_run(
        vault_file, "pass123", _py_print_env("EXTRA_VAR"), extra_env={"EXTRA_VAR": "bonus"}
    )
    assert result.stdout.strip() == "bonus"
