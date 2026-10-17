"""Digests of files and text, for integrity checks and content addressing."""

from __future__ import annotations

import hashlib
from os import PathLike
from pathlib import Path

_CHUNK = 1 << 20


def hash_file(path: str | PathLike[str], algorithm: str = "sha256") -> str:
    """Hex digest of a file's bytes, read in chunks.

    Args:
        path: The file.
        algorithm: Any name :mod:`hashlib` knows (``"sha256"``, ``"md5"``, ``"blake2b"``, ...).
    """
    digest = hashlib.new(algorithm)
    with Path(path).open("rb") as f:
        while chunk := f.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def hash_text(text: str, algorithm: str = "sha256", encoding: str = "utf-8") -> str:
    """Hex digest of a string's encoded bytes."""
    return hashlib.new(algorithm, text.encode(encoding)).hexdigest()


def verify_file(path: str | PathLike[str], expected: str, algorithm: str = "sha256") -> bool:
    """True if the file's digest equals ``expected`` (case-insensitive hex)."""
    return hash_file(path, algorithm).lower() == expected.strip().lower()
