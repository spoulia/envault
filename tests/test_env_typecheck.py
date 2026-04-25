"""Tests for envault.env_typecheck."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_typecheck import typecheck_cmd
from envault.env_typecheck import TypeCheckResult, has_issues, typecheck_env


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "PORT=8080\n"
        "RATIO=3.14\n"
        "DEBUG=true\n"
        "SITE_URL=https://example.com\n"
        "ADMIN_EMAIL=admin@example.com\n"
        "CONFIG={\"key\": 1}\n"
        "NAME=alice\n"
    )
    return p


def test_typecheck_returns_result_type(env_file: Path) -> None:
    result = typecheck_env(env_file, {"PORT": "int"})
    assert isinstance(result, TypeCheckResult)


def test_valid_int_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"PORT": "int"})
    assert not has_issues(result)
    assert result.checked == 1


def test_invalid_int_raises_issue(env_file: Path) -> None:
    result = typecheck_env(env_file, {"NAME": "int"})
    assert has_issues(result)
    assert result.issues[0].key == "NAME"
    assert result.issues[0].expected == "int"


def test_valid_float_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"RATIO": "float"})
    assert not has_issues(result)


def test_valid_bool_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"DEBUG": "bool"})
    assert not has_issues(result)


def test_invalid_bool_raises_issue(env_file: Path) -> None:
    result = typecheck_env(env_file, {"NAME": "bool"})
    assert has_issues(result)


def test_valid_url_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"SITE_URL": "url"})
    assert not has_issues(result)


def test_invalid_url_raises_issue(env_file: Path) -> None:
    result = typecheck_env(env_file, {"NAME": "url"})
    assert has_issues(result)


def test_valid_email_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"ADMIN_EMAIL": "email"})
    assert not has_issues(result)


def test_valid_json_passes(env_file: Path) -> None:
    result = typecheck_env(env_file, {"CONFIG": "json"})
    assert not has_issues(result)


def test_missing_key_is_skipped(env_file: Path) -> None:
    result = typecheck_env(env_file, {"NONEXISTENT": "int"})
    assert not has_issues(result)
    assert result.skipped == 1
    assert result.checked == 0


def test_unknown_type_is_skipped(env_file: Path) -> None:
    result = typecheck_env(env_file, {"PORT": "uuid"})
    assert result.skipped == 1


# ── CLI tests ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_check_passes(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    types_file = tmp_path / "types.json"
    types_file.write_text('{"PORT": "int", "DEBUG": "bool"}')
    result = runner.invoke(typecheck_cmd, ["check", str(env_file), "--types", str(types_file)])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_check_fails_strict(runner: CliRunner, env_file: Path, tmp_path: Path) -> None:
    types_file = tmp_path / "types.json"
    types_file.write_text('{"NAME": "int"}')
    result = runner.invoke(typecheck_cmd, ["check", str(env_file), "--types", str(types_file), "--strict"])
    assert result.exit_code == 1
    assert "NAME" in result.output


def test_init_outputs_json(runner: CliRunner, env_file: Path) -> None:
    result = runner.invoke(typecheck_cmd, ["init", str(env_file)])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert "PORT" in data
    assert data["PORT"] == "str"
