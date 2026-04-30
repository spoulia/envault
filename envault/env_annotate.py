"""env_annotate.py – attach and retrieve inline annotations for .env keys."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_FILE = Path(".envault_annotations.json")


@dataclass
class AnnotationEntry:
    key: str
    note: str
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class AnnotationResult:
    entries: List[AnnotationEntry]

    @property
    def count(self) -> int:
        return len(self.entries)

    def for_key(self, key: str) -> Optional[AnnotationEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def _load(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(data: Dict[str, dict], path: Path) -> None:
    path.write_text(json.dumps(data, indent=2))


def add_annotation(
    key: str,
    note: str,
    *,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    path: Path = _DEFAULT_FILE,
) -> AnnotationEntry:
    data = _load(path)
    if key in data:
        raise ValueError(f"Annotation for '{key}' already exists. Use update_annotation to change it.")
    entry = {"note": note, "author": author, "tags": tags or []}
    data[key] = entry
    _save(data, path)
    return AnnotationEntry(key=key, **entry)


def update_annotation(
    key: str,
    note: str,
    *,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    path: Path = _DEFAULT_FILE,
) -> AnnotationEntry:
    data = _load(path)
    if key not in data:
        raise KeyError(f"No annotation found for '{key}'.")
    data[key] = {"note": note, "author": author, "tags": tags or []}
    _save(data, path)
    return AnnotationEntry(key=key, **data[key])


def remove_annotation(key: str, *, path: Path = _DEFAULT_FILE) -> None:
    data = _load(path)
    if key not in data:
        raise KeyError(f"No annotation found for '{key}'.")
    del data[key]
    _save(data, path)


def get_annotations(*, path: Path = _DEFAULT_FILE) -> AnnotationResult:
    data = _load(path)
    entries = [AnnotationEntry(key=k, **v) for k, v in data.items()]
    return AnnotationResult(entries=entries)
