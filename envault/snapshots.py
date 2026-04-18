"""Snapshot management: save and restore named vault snapshots."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_DIR = Path(".envault_snapshots")
_META_FILE = SNAPSHOT_DIR / "meta.json"


def _load_meta() -> dict:
    if not _META_FILE.exists():
        return {}
    return json.loads(_META_FILE.read_text())


def _save_meta(meta: dict) -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    _META_FILE.write_text(json.dumps(meta, indent=2))


def save_snapshot(vault_path: Path, name: str, description: str = "") -> dict:
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")
    meta = _load_meta()
    if name in meta:
        raise ValueError(f"Snapshot '{name}' already exists.")
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    dest = SNAPSHOT_DIR / f"{name}.vault"
    shutil.copy2(vault_path, dest)
    entry = {
        "name": name,
        "description": description,
        "source": str(vault_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    meta[name] = entry
    _save_meta(meta)
    return entry


def restore_snapshot(name: str, target_path: Path) -> None:
    meta = _load_meta()
    if name not in meta:
        raise KeyError(f"Snapshot '{name}' not found.")
    src = SNAPSHOT_DIR / f"{name}.vault"
    shutil.copy2(src, Path(target_path))


def delete_snapshot(name: str) -> None:
    meta = _load_meta()
    if name not in meta:
        raise KeyError(f"Snapshot '{name}' not found.")
    (SNAPSHOT_DIR / f"{name}.vault").unlink(missing_ok=True)
    del meta[name]
    _save_meta(meta)


def list_snapshots() -> list[dict]:
    return list(_load_meta().values())


def get_snapshot(name: str) -> dict:
    meta = _load_meta()
    if name not in meta:
        raise KeyError(f"Snapshot '{name}' not found.")
    return meta[name]
