"""Split a .env file into fixed-size chunks for pagination or batch processing."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


@dataclass
class ChunkResult:
    chunks: List[Dict[str, str]]
    total_keys: int
    chunk_size: int
    source: str

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


def _parse_env(path: Path) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs[key.strip()] = value.strip()
    return pairs


def chunk_file(path: Path, chunk_size: int = 10) -> ChunkResult:
    """Split env file into chunks of *chunk_size* key-value pairs."""
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    pairs = _parse_env(path)
    items = list(pairs.items())
    chunks = [
        dict(items[i : i + chunk_size])
        for i in range(0, len(items), chunk_size)
    ]
    if not chunks:
        chunks = [{}]
    return ChunkResult(
        chunks=chunks,
        total_keys=len(items),
        chunk_size=chunk_size,
        source=str(path),
    )


def format_chunk(chunk: Dict[str, str], index: int) -> str:
    """Pretty-print a single chunk."""
    lines = [f"--- chunk {index + 1} ---"]
    for k, v in chunk.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines)
