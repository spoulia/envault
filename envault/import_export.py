"""Bulk import/export of .env variables to/from CSV or JSON formats."""
from __future__ import annotations
import csv
import json
import io
from pathlib import Path
from typing import Literal

Format = Literal["csv", "json"]


def _parse_env(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _render_env(data: dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items())) + "\n"


def export_env(env_path: Path, fmt: Format) -> str:
    """Export an .env file to CSV or JSON string."""
    if not env_path.exists():
        raise FileNotFoundError(f"{env_path} not found")
    data = _parse_env(env_path.read_text())
    if fmt == "json":
        return json.dumps(data, indent=2)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value"])
    for k, v in sorted(data.items()):
        writer.writerow([k, v])
    return buf.getvalue()


def import_env(env_path: Path, content: str, fmt: Format, merge: bool = False) -> int:
    """Import CSV or JSON content into an .env file. Returns count of keys written."""
    if fmt == "json":
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON must be a flat object")
    else:
        reader = csv.DictReader(io.StringIO(content))
        if reader.fieldnames is None or "key" not in reader.fieldnames:
            raise ValueError("CSV must have 'key' and 'value' columns")
        data = {row["key"]: row["value"] for row in reader}

    if merge and env_path.exists():
        existing = _parse_env(env_path.read_text())
        existing.update(data)
        data = existing

    env_path.write_text(_render_env(data))
    return len(data)
