"""Checks that answer "is this safe or well-formed?" without raising.

Most functions return a :class:`ValidationResult`, which is truthy when valid
and carries a message. The path checks are about user-supplied names landing
somewhere they shouldn't.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass
class ValidationResult:
    """Outcome of a check. Truthy when valid.

    Attributes:
        is_valid: Whether the check passed.
        message: One line saying why, or what passed.
        errors: Individual problems, when a check can find several.
    """

    is_valid: bool
    message: str = ""
    errors: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid


_DANGEROUS = re.compile(r'[<>:"|?*\x00-\x1f]')
_RESERVED = (
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


def has_path_traversal(path: str) -> bool:
    """True if any component of ``path`` is ``..``."""
    return ".." in Path(path).parts or ".." in path.replace("\\", "/").split("/")


def contains_dangerous_chars(path: str) -> bool:
    """True if ``path`` has characters invalid in filenames on Windows or control characters."""
    return _DANGEROUS.search(path) is not None


def is_safe_path(path: str | PathLike[str], base: str | PathLike[str] | None = None) -> bool:
    """True if ``path`` has no traversal or dangerous characters and, given ``base``, resolves inside it."""
    text = str(path)
    if has_path_traversal(text) or contains_dangerous_chars(text):
        return False
    if base is not None:
        try:
            return Path(path).resolve().is_relative_to(Path(base).resolve())
        except OSError:
            return False
    return True


def sanitize_filename(name: str, replacement: str = "_", max_length: int = 255) -> str:
    """Make a string safe to use as a single filename.

    Path separators, dangerous characters, and runs of dots become
    ``replacement``, leading and trailing dots and spaces go, Windows reserved
    names get a prefix, and
    the result is cut to ``max_length`` keeping the extension. Empty input
    gives ``"unnamed"``.
    """
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, name)
    cleaned = re.sub(r"\.{2,}", replacement, cleaned).strip(". ")
    if not cleaned.strip(replacement):  # nothing, or nothing but replacements
        return "unnamed"
    if Path(cleaned).stem.upper() in _RESERVED:
        cleaned = f"{replacement}{cleaned}"
    if len(cleaned) > max_length:
        p = Path(cleaned)
        keep = max_length - len(p.suffix)
        cleaned = p.stem[:keep] + p.suffix
    return cleaned


def validate_file_path(
    path: str | None, must_exist: bool = True, max_length: int = 4096
) -> ValidationResult:
    """Check a path string for emptiness, length, traversal, and optionally existence."""
    if not path:
        return ValidationResult(False, "Path is empty")
    if len(path) > max_length:
        return ValidationResult(False, f"Path is longer than {max_length} characters")
    if has_path_traversal(path):
        return ValidationResult(False, "Path contains '..'")
    if contains_dangerous_chars(path):
        return ValidationResult(False, "Path contains characters not allowed in filenames")
    if must_exist and not Path(path).exists():
        return ValidationResult(False, f"Path does not exist: {path}")
    return ValidationResult(True, "Path is valid")


def validate_file_extension(path: str | PathLike[str], allowed: Iterable[str]) -> ValidationResult:
    """Check the extension is one of ``allowed`` (with or without dots, any case)."""
    ext = Path(path).suffix.lower()
    wanted = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in allowed}
    if not ext:
        return ValidationResult(False, "File has no extension")
    if ext not in wanted:
        return ValidationResult(
            False, f"Extension {ext!r} is not allowed; expected one of {sorted(wanted)}"
        )
    return ValidationResult(True, f"Extension {ext!r} is allowed")


def validate_file_size(
    path: str | PathLike[str], max_bytes: int | None = None, min_bytes: int = 0
) -> ValidationResult:
    """Check an existing file's size is within ``[min_bytes, max_bytes]``."""
    target = Path(path)
    if not target.is_file():
        return ValidationResult(False, f"File does not exist: {target}")
    size = target.stat().st_size
    if size < min_bytes:
        return ValidationResult(
            False, f"File is {size} bytes, smaller than the minimum {min_bytes}"
        )
    if max_bytes is not None and size > max_bytes:
        return ValidationResult(False, f"File is {size} bytes, larger than the maximum {max_bytes}")
    return ValidationResult(True, f"File is {size} bytes")


def validate_url(url: str, schemes: Iterable[str] = ("http", "https")) -> ValidationResult:
    """Check a URL has an allowed scheme and a host."""
    if not url:
        return ValidationResult(False, "URL is empty")
    parsed = urlparse(url)
    if parsed.scheme not in set(schemes):
        return ValidationResult(False, f"URL scheme {parsed.scheme or 'missing'!r} is not allowed")
    if not parsed.netloc:
        return ValidationResult(False, "URL has no host")
    return ValidationResult(True, "URL is valid")


_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def validate_email(email: str) -> ValidationResult:
    """Check an address looks like ``name@domain.tld``. Not a deliverability check."""
    if _EMAIL.match(email or ""):
        return ValidationResult(True, "Email is valid")
    return ValidationResult(False, "Email is not well-formed")


def validate_json_structure(
    data: str | bytes | Mapping[str, Any],
    required: Iterable[str] = (),
    types: Mapping[str, type | tuple[type, ...]] | None = None,
) -> ValidationResult:
    """Check JSON (text or an already-parsed mapping) has required keys of the right types.

    Keys may be dotted for nesting. Every problem found is listed in ``errors``.
    """
    from novus_pytils.config import get_value

    if isinstance(data, (str, bytes)):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return ValidationResult(False, f"Invalid JSON: {e}")
    if not isinstance(data, Mapping):
        return ValidationResult(False, "JSON top level must be an object")
    sentinel = object()
    errors = [
        f"Missing required key: {k}" for k in required if get_value(data, k, sentinel) is sentinel
    ]
    for key, expected in (types or {}).items():
        value = get_value(data, key, sentinel)
        if value is not sentinel and not isinstance(value, expected):
            names = (
                expected.__name__
                if isinstance(expected, type)
                else "/".join(t.__name__ for t in expected)
            )
            errors.append(f"Key {key!r} should be {names}, got {type(value).__name__}")
    if errors:
        return ValidationResult(False, f"{len(errors)} problem(s) found", errors)
    return ValidationResult(True, "JSON structure is valid")


def check_disk_space(path: str | PathLike[str], required_bytes: int) -> ValidationResult:
    """Check the filesystem holding ``path`` has at least ``required_bytes`` free."""
    try:
        _total, _used, free = shutil.disk_usage(path)
    except OSError as e:
        return ValidationResult(False, f"Cannot check disk space: {e}")
    mib = 1 << 20
    if free < required_bytes:
        return ValidationResult(
            False,
            f"Insufficient disk space: {free / mib:.1f} MiB free, {required_bytes / mib:.1f} MiB needed",
        )
    return ValidationResult(True, f"{free / mib:.1f} MiB free")
