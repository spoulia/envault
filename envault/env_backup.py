"""Backup and restore .env files with timestamped copies."""
from __future__ import annotations

import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

BACKUP_DIR = Path(".envault_backups")


@dataclass
class BackupEntry:
    name: str
    source: str
    timestamp: float
    path: str


@dataclass
class BackupResult:
    source: str
    backup_path: str
    timestamp: float


def _ensure_dir() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    return BACKUP_DIR


def create_backup(source: str | Path) -> BackupResult:
    """Copy *source* into the backup directory with a timestamp suffix."""
    src = Path(source)
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    ts = time.time()
    stamp = int(ts)
    dest = _ensure_dir() / f"{src.stem}_{stamp}{src.suffix}"
    shutil.copy2(src, dest)
    return BackupResult(source=str(src), backup_path=str(dest), timestamp=ts)


def list_backups(source: str | Path | None = None) -> list[BackupEntry]:
    """Return all backups, optionally filtered by original source stem."""
    if not BACKUP_DIR.exists():
        return []
    entries: list[BackupEntry] = []
    for p in sorted(BACKUP_DIR.iterdir()):
        if not p.is_file():
            continue
        # name pattern: stem_timestamp.suffix
        parts = p.stem.rsplit("_", 1)
        if len(parts) != 2:
            continue
        stem, ts_str = parts
        try:
            ts = float(ts_str)
        except ValueError:
            continue
        if source and Path(source).stem != stem:
            continue
        entries.append(BackupEntry(name=p.name, source=stem, timestamp=ts, path=str(p)))
    return entries


def restore_backup(backup_name: str, destination: str | Path) -> None:
    """Overwrite *destination* with the named backup file."""
    src = BACKUP_DIR / backup_name
    if not src.exists():
        raise FileNotFoundError(f"Backup not found: {backup_name}")
    shutil.copy2(src, destination)


def delete_backup(backup_name: str) -> None:
    """Delete a single backup entry."""
    target = BACKUP_DIR / backup_name
    if not target.exists():
        raise FileNotFoundError(f"Backup not found: {backup_name}")
    target.unlink()
