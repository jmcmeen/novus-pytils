"""Which kind of file is this? A registry of extensions by kind, and lookups on it.

The kinds are ``audio``, ``image``, ``video``, ``text``, and ``archive``.
"""

from __future__ import annotations

from collections.abc import Iterable
from os import PathLike
from pathlib import Path

from novus_pytils.files import get_files_by_extension

KINDS: dict[str, frozenset[str]] = {
    "audio": frozenset({".wav", ".mp3", ".ogg", ".flac", ".aac", ".wma", ".m4a", ".opus", ".aiff"}),
    "image": frozenset({".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg"}),
    "video": frozenset({".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"}),
    "text": frozenset(
        {
            ".txt",
            ".md",
            ".markdown",
            ".csv",
            ".tsv",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".log",
        }
    ),
    "archive": frozenset({".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z"}),
}
"""Lowercase extensions (with the dot) by kind."""


def extensions_for(kind: str) -> frozenset[str]:
    """The extensions registered under ``kind``.

    Raises:
        KeyError: If ``kind`` is not one of :data:`KINDS`.
    """
    return KINDS[kind]


def kind_of(path: str | PathLike[str]) -> str | None:
    """The kind a path belongs to by its extension, or ``None`` if unregistered."""
    ext = Path(path).suffix.lower()
    for kind, exts in KINDS.items():
        if ext in exts:
            return kind
    return None


def is_kind(path: str | PathLike[str], kind: str) -> bool:
    """True if the path's extension is registered under ``kind``."""
    return Path(path).suffix.lower() in extensions_for(kind)


def get_files(
    directory: str | PathLike[str],
    kind: str | None = None,
    extensions: str | Iterable[str] | None = None,
    recursive: bool = False,
) -> list[Path]:
    """Files in a directory filtered by kind, by explicit extensions, or both.

    Args:
        directory: Where to look.
        kind: One of :data:`KINDS`; keeps files of that kind.
        extensions: Explicit extensions to keep, with or without the dot.
            Combined with ``kind`` the file must match either.
        recursive: Search subdirectories too.

    Returns:
        Sorted paths. With neither ``kind`` nor ``extensions`` given, every file.
    """
    wanted: set[str] = set()
    if kind is not None:
        wanted |= extensions_for(kind)
    if extensions is not None:
        exts = [extensions] if isinstance(extensions, str) else list(extensions)
        wanted |= {e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts}
    if not wanted:
        from novus_pytils.files import list_files

        return list_files(directory, recursive)
    return get_files_by_extension(directory, wanted, recursive)
