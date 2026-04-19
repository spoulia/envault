"""Pin specific env keys to fixed values, preventing accidental overwrite."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

DEFAULT_PIN_FILE = Path(".envault_pins.json")


@dataclass
class PinResult:
    pinned: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)


def _load_pins(pin_file: Path) -> Dict[str, str]:
    if not pin_file.exists():
        return {}
    return json.loads(pin_file.read_text())


def _save_pins(pins: Dict[str, str], pin_file: Path) -> None:
    pin_file.write_text(json.dumps(pins, indent=2))


def pin_key(key: str, value: str, pin_file: Path = DEFAULT_PIN_FILE) -> None:
    pins = _load_pins(pin_file)
    pins[key] = value
    _save_pins(pins, pin_file)


def unpin_key(key: str, pin_file: Path = DEFAULT_PIN_FILE) -> bool:
    pins = _load_pins(pin_file)
    if key not in pins:
        return False
    del pins[key]
    _save_pins(pins, pin_file)
    return True


def list_pins(pin_file: Path = DEFAULT_PIN_FILE) -> Dict[str, str]:
    return _load_pins(pin_file)


def check_violations(env_file: Path, pin_file: Path = DEFAULT_PIN_FILE) -> PinResult:
    """Check whether pinned keys in env_file match their pinned values."""
    pins = _load_pins(pin_file)
    result = PinResult()
    if not env_file.exists():
        return result
    env: Dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    for key, expected in pins.items():
        if key in env:
            if env[key] != expected:
                result.violations.append(key)
            else:
                result.pinned.append(key)
        else:
            result.skipped.append(key)
    return result
