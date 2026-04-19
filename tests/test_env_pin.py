import pytest
from pathlib import Path
from envault.env_pin import pin_key, unpin_key, list_pins, check_violations


@pytest.fixture
def pin_file(tmp_path):
    return tmp_path / "pins.json"


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret123\nDEBUG=false\n")
    return f


def test_pin_key_creates_entry(pin_file):
    pin_key("API_KEY", "secret123", pin_file)
    pins = list_pins(pin_file)
    assert pins["API_KEY"] == "secret123"


def test_pin_key_persists(pin_file):
    pin_key("FOO", "bar", pin_file)
    pin_key("BAZ", "qux", pin_file)
    pins = list_pins(pin_file)
    assert len(pins) == 2


def test_unpin_key_removes_entry(pin_file):
    pin_key("API_KEY", "secret123", pin_file)
    result = unpin_key("API_KEY", pin_file)
    assert result is True
    assert "API_KEY" not in list_pins(pin_file)


def test_unpin_missing_key_returns_false(pin_file):
    result = unpin_key("MISSING", pin_file)
    assert result is False


def test_list_pins_empty_when_no_file(pin_file):
    assert list_pins(pin_file) == {}


def test_check_violations_no_violations(env_file, pin_file):
    pin_key("API_KEY", "secret123", pin_file)
    result = check_violations(env_file, pin_file)
    assert "API_KEY" in result.pinned
    assert result.violations == []


def test_check_violations_detects_mismatch(env_file, pin_file):
    pin_key("API_KEY", "wrong_value", pin_file)
    result = check_violations(env_file, pin_file)
    assert "API_KEY" in result.violations
    assert result.pinned == []


def test_check_violations_skips_missing_key(env_file, pin_file):
    pin_key("NOT_IN_FILE", "value", pin_file)
    result = check_violations(env_file, pin_file)
    assert "NOT_IN_FILE" in result.skipped


def test_check_violations_missing_env_file(tmp_path, pin_file):
    pin_key("KEY", "val", pin_file)
    result = check_violations(tmp_path / "nonexistent.env", pin_file)
    assert result.violations == []
    assert result.pinned == []
