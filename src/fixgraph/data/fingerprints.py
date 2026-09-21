"""Asset hashing and checksum fingerprint utilities."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union


def compute_sha256_bytes(data: bytes) -> str:
    """Return hex sha256 of byte array."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_string(text: str) -> str:
    """Return hex sha256 of string."""
    return compute_sha256_bytes(text.encode("utf-8"))


def compute_sha256_file(file_path: Union[str, Path]) -> str:
    """Return hex sha256 digest of a file if it exists, else return empty string."""
    path = Path(file_path)
    if not path.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_sha256_json(data: Any) -> str:
    """Return hex sha256 of serialized deterministic JSON."""
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return compute_sha256_string(serialized)
