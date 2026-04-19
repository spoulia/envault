"""Tests for envault.env_generate."""
import pytest
from pathlib import Path

from envault.env_generate import KeySpec, generate


@pytest.fixture
def env_file(tmp_path) -> Path:
    return tmp_path / ".env"


def test_generate_creates_file(env_file):
    specs = [KeySpec(name="APP_NAME", default="myapp")]
    result = generate(specs, str(env_file))
    assert env_file.exists()
    assert "APP_NAME=myapp" in env_file.read_text()
    assert "APP_NAME" in result.generated


def test_generate_secret_key_is_random(env_file):
    specs = [KeySpec(name="SECRET_KEY", secret=True, secret_length=24)]
    generate(specs, str(env_file))
    content = env_file.read_text()
    line = next(l for l in content.splitlines() if l.startswith("SECRET_KEY="))
    value = line.split("=", 1)[1]
    assert len(value) == 24


def test_generate_two_secrets_differ(env_file, tmp_path):
    specs = [KeySpec(name="SECRET_KEY", secret=True)]
    env_b = tmp_path / ".env.b"
    generate(specs, str(env_file))
    generate(specs, str(env_b))
    val_a = [l for l in env_file.read_text().splitlines() if l.startswith("SECRET_KEY=")][0]
    val_b = [l for l in env_b.read_text().splitlines() if l.startswith("SECRET_KEY=")][0]
    assert val_a != val_b


def test_generate_skips_existing_without_overwrite(env_file):
    env_file.write_text("DB_URL=postgres://old\n")
    specs = [KeySpec(name="DB_URL", default="postgres://new")]
    result = generate(specs, str(env_file), overwrite=False)
    assert "DB_URL" in result.skipped
    assert "postgres://old" in env_file.read_text()


def test_generate_overwrites_when_flag_set(env_file):
    env_file.write_text("DB_URL=postgres://old\n")
    specs = [KeySpec(name="DB_URL", default="postgres://new")]
    result = generate(specs, str(env_file), overwrite=True)
    assert "DB_URL" in result.generated
    assert "postgres://new" in env_file.read_text()


def test_generate_comment_written(env_file):
    specs = [KeySpec(name="PORT", default="8080", comment="HTTP listen port")]
    generate(specs, str(env_file))
    content = env_file.read_text()
    assert "# HTTP listen port" in content


def test_generate_multiple_keys(env_file):
    specs = [
        KeySpec(name="A", default="1"),
        KeySpec(name="B", default="2"),
        KeySpec(name="C", secret=True),
    ]
    result = generate(specs, str(env_file))
    assert set(result.generated) == {"A", "B", "C"}
    content = env_file.read_text()
    assert "A=1" in content
    assert "B=2" in content
