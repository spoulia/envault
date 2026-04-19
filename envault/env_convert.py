"""Convert .env files between formats (dotenv, json, yaml, toml)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Literal

Format = Literal["dotenv", "json", "yaml", "toml"]


@dataclass
class ConvertResult:
    source_format: str
    target_format: str
    keys_converted: int
    output_path: str
    warnings: list[str] = field(default_factory=list)


def _parse_dotenv(text: str) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _render_dotenv(data: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in data.items()) + "\n"


def _render_json(data: Dict[str, str]) -> str:
    return json.dumps(data, indent=2) + "\n"


def _render_yaml(data: Dict[str, str]) -> str:
    lines = []
    for k, v in data.items():
        safe_v = f'"{v}"' if any(c in v for c in ': #{}[]') else v
        lines.append(f"{k}: {safe_v}")
    return "\n".join(lines) + "\n"


def _render_toml(data: Dict[str, str]) -> str:
    lines = []
    for k, v in data.items():
        lines.append(f'{k} = "{v}"')
    return "\n".join(lines) + "\n"


_RENDERERS = {
    "dotenv": _render_dotenv,
    "json": _render_json,
    "yaml": _render_yaml,
    "toml": _render_toml,
}


def convert_env(src: str | Path, dest: str | Path, target_format: Format) -> ConvertResult:
    src, dest = Path(src), Path(dest)
    if not src.exists():
        raise FileNotFoundError(f"{src} not found")
    data = _parse_dotenv(src.read_text())
    renderer = _RENDERERS.get(target_format)
    if renderer is None:
        raise ValueError(f"Unsupported format: {target_format}")
    dest.write_text(renderer(data))
    return ConvertResult(
        source_format="dotenv",
        target_format=target_format,
        keys_converted=len(data),
        output_path=str(dest),
    )
