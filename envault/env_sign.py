"""env_sign.py – HMAC-based signing and verification of .env files."""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from pathlib import Path

_SIG_VERSION = 1


@dataclass
class SignResult:
    file: str
    signature: str
    algorithm: str = "sha256"
    version: int = _SIG_VERSION


@dataclass
class VerifyResult:
    file: str
    valid: bool
    reason: str = ""


def _file_digest(path: Path, secret: str) -> str:
    """Return an HMAC-SHA256 hex digest of *path* keyed with *secret*."""
    raw = path.read_bytes()
    return hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()


def sign_file(env_path: str | Path, secret: str, sig_path: str | Path | None = None) -> SignResult:
    """Sign *env_path* and write a JSON signature file next to it."""
    env_path = Path(env_path)
    if not env_path.exists():
        raise FileNotFoundError(f"env file not found: {env_path}")

    digest = _file_digest(env_path, secret)
    result = SignResult(file=str(env_path), signature=digest)

    sig_path = Path(sig_path) if sig_path else env_path.with_suffix(".sig")
    sig_path.write_text(
        json.dumps(
            {"file": result.file, "signature": digest, "algorithm": result.algorithm, "version": result.version},
            indent=2,
        )
    )
    return result


def verify_file(env_path: str | Path, secret: str, sig_path: str | Path | None = None) -> VerifyResult:
    """Verify *env_path* against its signature file."""
    env_path = Path(env_path)
    sig_path = Path(sig_path) if sig_path else env_path.with_suffix(".sig")

    if not env_path.exists():
        return VerifyResult(file=str(env_path), valid=False, reason="env file not found")
    if not sig_path.exists():
        return VerifyResult(file=str(env_path), valid=False, reason="signature file not found")

    try:
        meta = json.loads(sig_path.read_text())
        stored_sig = meta["signature"]
    except (json.JSONDecodeError, KeyError) as exc:
        return VerifyResult(file=str(env_path), valid=False, reason=f"invalid signature file: {exc}")

    expected = _file_digest(env_path, secret)
    if hmac.compare_digest(expected, stored_sig):
        return VerifyResult(file=str(env_path), valid=True)
    return VerifyResult(file=str(env_path), valid=False, reason="signature mismatch")
