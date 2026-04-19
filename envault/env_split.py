"""Split a .env file into multiple files by prefix or key list."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    files_written: List[str] = field(default_factory=list)
    keys_split: int = 0
    keys_unmatched: int = 0


def _parse_env(text: str) -> List[tuple]:
    pairs = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def _render_env(pairs: List[tuple]) -> str:
    return "\n".join(f"{k}={v}" for k, v in pairs) + ("\n" if pairs else "")


def split_by_prefix(
    source: Path,
    output_dir: Path,
    prefixes: List[str],
    remainder_file: Optional[str] = None,
) -> SplitResult:
    """Split source .env into files per prefix."""
    pairs = _parse_env(source.read_text())
    output_dir.mkdir(parents=True, exist_ok=True)
    buckets: Dict[str, List[tuple]] = {p: [] for p in prefixes}
    remainder: List[tuple] = []

    for key, value in pairs:
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                buckets[prefix].append((key, value))
                matched = True
                break
        if not matched:
            remainder.append((key, value))

    result = SplitResult()
    for prefix, bucket_pairs in buckets.items():
        if not bucket_pairs:
            continue
        out_path = output_dir / f"{prefix.lower().rstrip('_')}.env"
        out_path.write_text(_render_env(bucket_pairs))
        result.files_written.append(str(out_path))
        result.keys_split += len(bucket_pairs)

    result.keys_unmatched = len(remainder)
    if remainder and remainder_file:
        rem_path = output_dir / remainder_file
        rem_path.write_text(_render_env(remainder))
        result.files_written.append(str(rem_path))

    return result
