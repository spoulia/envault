"""Tests for envault.env_classify."""
import pytest
from pathlib import Path

from envault.env_classify import (
    ClassifyResult,
    classify_file,
    format_classify,
)


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PASSWORD=secret123\n"
        "API_KEY=abc\n"
        "APP_PORT=8080\n"
        "ENABLE_FEATURE_X=true\n"
        "LOG_LEVEL=debug\n"
        "APP_NAME=myapp\n"
        "STATIC_DIR=/var/static\n"
    )
    return p


def test_classify_returns_classify_result_type(env_file: Path) -> None:
    result = classify_file(env_file)
    assert isinstance(result, ClassifyResult)


def test_total_keys_count(env_file: Path) -> None:
    result = classify_file(env_file)
    assert result.total_keys == 8


def test_database_category_detected(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "database" in result.categories
    assert "DB_HOST" in result.categories["database"]


def test_secret_category_detected(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "secret" in result.categories
    keys = result.categories["secret"]
    assert "DB_PASSWORD" in keys or "API_KEY" in keys


def test_network_category_detected(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "network" in result.categories
    assert "APP_PORT" in result.categories["network"]


def test_feature_flag_category_detected(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "feature_flag" in result.categories
    assert "ENABLE_FEATURE_X" in result.categories["feature_flag"]


def test_path_category_detected(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "path" in result.categories
    assert "STATIC_DIR" in result.categories["path"]


def test_unclassified_keys_present(env_file: Path) -> None:
    result = classify_file(env_file)
    assert "APP_NAME" in result.unclassified


def test_classified_count_plus_unclassified_equals_total(env_file: Path) -> None:
    result = classify_file(env_file)
    assert result.classified_count + result.unclassified_count == result.total_keys


def test_format_classify_contains_category_header(env_file: Path) -> None:
    result = classify_file(env_file)
    output = format_classify(result)
    assert "[database]" in output


def test_format_classify_contains_unclassified_section(env_file: Path) -> None:
    result = classify_file(env_file)
    output = format_classify(result)
    assert "[unclassified]" in output
    assert "APP_NAME" in output


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        classify_file(tmp_path / "missing.env")


def test_empty_file_returns_zero_keys(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("")
    result = classify_file(p)
    assert result.total_keys == 0
    assert result.classified_count == 0
    assert result.unclassified_count == 0
