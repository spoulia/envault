import pytest
from pathlib import Path
from envault.vault import lock
from envault.env_set import set_keys, unset_keys, list_keys

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / "test.vault"
    lock(vf, "KEY1=value1\nKEY2=value2\n", PASSWORD)
    return vf


def test_set_new_key(vault_file):
    result = set_keys(vault_file, PASSWORD, {"KEY3": "value3"})
    assert "KEY3" in result.set
    pairs = list_keys(vault_file, PASSWORD)
    assert pairs["KEY3"] == "value3"


def test_set_overwrites_existing(vault_file):
    result = set_keys(vault_file, PASSWORD, {"KEY1": "new"}, overwrite=True)
    assert "KEY1" in result.set
    assert list_keys(vault_file, PASSWORD)["KEY1"] == "new"


def test_set_skips_when_no_overwrite(vault_file):
    result = set_keys(vault_file, PASSWORD, {"KEY1": "new"}, overwrite=False)
    assert "KEY1" in result.skipped
    assert list_keys(vault_file, PASSWORD)["KEY1"] == "value1"


def test_set_multiple_keys(vault_file):
    result = set_keys(vault_file, PASSWORD, {"A": "1", "B": "2"})
    assert sorted(result.set) == ["A", "B"]
    pairs = list_keys(vault_file, PASSWORD)
    assert pairs["A"] == "1" and pairs["B"] == "2"


def test_unset_existing_key(vault_file):
    result = unset_keys(vault_file, PASSWORD, ["KEY1"])
    assert "KEY1" in result.unset
    assert "KEY1" not in list_keys(vault_file, PASSWORD)


def test_unset_missing_key(vault_file):
    result = unset_keys(vault_file, PASSWORD, ["MISSING"])
    assert "MISSING" in result.skipped


def test_list_keys_returns_all(vault_file):
    pairs = list_keys(vault_file, PASSWORD)
    assert pairs == {"KEY1": "value1", "KEY2": "value2"}


def test_set_wrong_password_raises(vault_file):
    from envault.crypto import decrypt
    with pytest.raises(Exception):
        set_keys(vault_file, "wrongpass", {"X": "y"})
