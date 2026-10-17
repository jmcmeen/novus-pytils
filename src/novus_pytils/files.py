"""Files and directories: reading, writing, copying, finding, syncing.

Thin, predictable wrappers over :mod:`pathlib` and :mod:`shutil`. Every
function accepts ``str`` or :class:`~pathlib.Path` and returns
:class:`~pathlib.Path` objects for anything path-like. For the attributes a
``Path`` already has (``suffix``, ``stem``, ``parent``, ``stat()``,
``rename()``, ``chmod()``) use the ``Path``.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from datetime import datetime
from os import PathLike
from pathlib import Path

StrPath = str | PathLike[str]

# --- single files ----------------------------------------------------------


def read_file_bytes(path: StrPath) -> bytes:
    """Return the whole file as bytes."""
    return Path(path).read_bytes()


def read_file_text(path: StrPath, encoding: str = "utf-8") -> str:
    """Return the whole file as text."""
    return Path(path).read_text(encoding=encoding)


def write_file(path: StrPath, content: str | bytes, encoding: str = "utf-8") -> Path:
    """Write ``content`` to ``path``, creating parent directories, replacing any existing file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding=encoding)
    return target


def append_to_file(path: StrPath, content: str, encoding: str = "utf-8") -> Path:
    """Append text to ``path``, creating it (and parents) if needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding=encoding) as f:
        f.write(content)
    return target


def get_file_size(path: StrPath) -> int:
    """Size of the file in bytes."""
    return Path(path).stat().st_size


def is_file_empty(path: StrPath) -> bool:
    """True if the file has no bytes."""
    return get_file_size(path) == 0


def file_exists(path: StrPath) -> bool:
    """True if ``path`` exists and is a regular file (not a directory)."""
    return Path(path).is_file()


def delete_file(path: StrPath) -> bool:
    """Delete a file if it exists. Returns whether anything was deleted.

    Raises:
        IsADirectoryError: If ``path`` is a directory; use :func:`delete_directory`.
    """
    target = Path(path)
    if target.is_dir():
        raise IsADirectoryError(f"{target} is a directory; use delete_directory()")
    if target.exists():
        target.unlink()
        return True
    return False


def copy_file(src: StrPath, dest: StrPath) -> Path:
    """Copy a file, keeping its metadata, creating ``dest``'s parent if needed."""
    target = Path(dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)
    return target


def copy_files(
    srcs: Iterable[StrPath], dest_dir: StrPath, enumerate_dups: bool = True
) -> list[Path]:
    """Copy files into a directory.

    Args:
        srcs: Files to copy.
        dest_dir: Directory to copy into; created if missing.
        enumerate_dups: When a name is already taken, write ``name_1.ext``,
            ``name_2.ext``, ... instead of overwriting.

    Returns:
        The paths written, in order.
    """
    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for src in srcs:
        src = Path(src)
        target = directory / src.name
        if enumerate_dups:
            counter = 1
            while target.exists():
                target = directory / f"{src.stem}_{counter}{src.suffix}"
                counter += 1
        shutil.copy2(src, target)
        written.append(target)
    return written


def move_file(src: StrPath, dest: StrPath) -> Path:
    """Move (or rename) a file, replacing ``dest`` if it exists."""
    target = Path(dest)
    target.parent.mkdir(parents=True, exist_ok=True)
    return Path(shutil.move(str(src), str(target)))


def download_file(url: str, save_to: StrPath, timeout: float = 60.0) -> Path:
    """Download ``url`` to ``save_to``, streaming to disk.

    Raises:
        requests.HTTPError: On a non-2xx response.
    """
    import requests

    target = Path(save_to)
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with target.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 16):
                f.write(chunk)
    return target


def create_backup(path: StrPath, backup_to: StrPath | None = None, suffix: str = ".bak") -> Path:
    """Copy a file to ``<name><suffix>``, beside it or inside ``backup_to``.

    Returns:
        The backup's path.
    """
    source = Path(path)
    if backup_to is None:
        target = source.with_name(source.name + suffix)
    else:
        directory = Path(backup_to)
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (source.name + suffix)
    shutil.copy2(source, target)
    return target


def restore_backup(backup: StrPath, original: StrPath | None = None, suffix: str = ".bak") -> Path:
    """Copy a backup back over the original.

    Args:
        backup: The backup file.
        original: Where to restore to. Defaults to the backup's name with
            ``suffix`` removed, in the same directory.
    """
    source = Path(backup)
    if original is None:
        if not source.name.endswith(suffix):
            raise ValueError(f"{source.name} does not end with {suffix!r}; pass original=")
        target = source.with_name(source.name[: -len(suffix)])
    else:
        target = Path(original)
    shutil.copy2(source, target)
    return target


# --- filtering lists of files -----------------------------------------------


def filter_files_by_size(
    files: Iterable[StrPath], min_size: int = 0, max_size: int | None = None
) -> list[Path]:
    """Keep the existing files whose size in bytes is within ``[min_size, max_size]``."""
    kept = []
    for f in files:
        p = Path(f)
        if not p.is_file():
            continue
        size = p.stat().st_size
        if size >= min_size and (max_size is None or size <= max_size):
            kept.append(p)
    return kept


def filter_files_by_date(
    files: Iterable[StrPath], after: datetime | None = None, before: datetime | None = None
) -> list[Path]:
    """Keep the existing files last modified within ``[after, before]``."""
    kept = []
    for f in files:
        p = Path(f)
        if not p.is_file():
            continue
        modified = datetime.fromtimestamp(p.stat().st_mtime)
        if (after is None or modified >= after) and (before is None or modified <= before):
            kept.append(p)
    return kept


# --- finding things in directories --------------------------------------------


def _normalize_extensions(extensions: Iterable[str]) -> set[str]:
    return {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}


def list_files(directory: StrPath, recursive: bool = True) -> list[Path]:
    """All regular files under ``directory``, sorted. Missing directory gives ``[]``."""
    root = Path(directory)
    if not root.is_dir():
        return []
    pattern = "**/*" if recursive else "*"
    return sorted(p for p in root.glob(pattern) if p.is_file())


def list_dirs(directory: StrPath, recursive: bool = True) -> list[Path]:
    """All directories under ``directory``, sorted. Missing directory gives ``[]``."""
    root = Path(directory)
    if not root.is_dir():
        return []
    pattern = "**/*" if recursive else "*"
    return sorted(p for p in root.glob(pattern) if p.is_dir())


def get_files_by_extension(
    directory: StrPath, extensions: str | Iterable[str], recursive: bool = False
) -> list[Path]:
    """Files under ``directory`` whose suffix is one of ``extensions``, case-insensitive.

    Args:
        directory: Where to look. Missing directory gives ``[]``.
        extensions: One extension or several, with or without the leading dot.
        recursive: Search subdirectories too.
    """
    wanted = _normalize_extensions([extensions] if isinstance(extensions, str) else extensions)
    return [p for p in list_files(directory, recursive) if p.suffix.lower() in wanted]


def find_files(directory: StrPath, substring: str, recursive: bool = True) -> list[Path]:
    """Files whose name contains ``substring``, case-insensitive."""
    needle = substring.casefold()
    return [p for p in list_files(directory, recursive) if needle in p.name.casefold()]


def find_dirs(directory: StrPath, substring: str, recursive: bool = True) -> list[Path]:
    """Directories whose name contains ``substring``, case-insensitive."""
    needle = substring.casefold()
    return [p for p in list_dirs(directory, recursive) if needle in p.name.casefold()]


def directory_contains_file(directory: StrPath, substring: str) -> bool:
    """True if any file under ``directory`` has ``substring`` in its name."""
    return bool(find_files(directory, substring))


def directory_contains_directory(directory: StrPath, substring: str) -> bool:
    """True if any directory under ``directory`` has ``substring`` in its name."""
    return bool(find_dirs(directory, substring))


def directory_contains_file_with_extension(directory: StrPath, extension: str) -> bool:
    """True if any file under ``directory`` (recursively) has the extension."""
    return bool(get_files_by_extension(directory, extension, recursive=True))


def count_files(directory: StrPath, recursive: bool = False) -> int:
    """Number of regular files in ``directory``."""
    return len(list_files(directory, recursive))


def get_subdirectories(directory: StrPath) -> list[Path]:
    """Immediate subdirectories of ``directory``, sorted."""
    return list_dirs(directory, recursive=False)


# --- whole directories --------------------------------------------------------


def create_directory(path: StrPath) -> Path:
    """Create a directory and any missing parents; fine if it already exists."""
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def directory_exists(path: StrPath) -> bool:
    """True if ``path`` exists and is a directory."""
    return Path(path).is_dir()


def delete_directory(path: StrPath) -> bool:
    """Delete a directory tree if it exists. Returns whether anything was deleted."""
    target = Path(path)
    if target.is_dir():
        shutil.rmtree(target)
        return True
    return False


def recreate_directory(path: StrPath) -> Path:
    """Delete a directory tree (if present) and create it empty."""
    delete_directory(path)
    return create_directory(path)


def copy_directory(src: StrPath, dest: StrPath) -> Path:
    """Copy a directory tree. ``dest`` may already exist; files are overwritten."""
    return Path(shutil.copytree(src, dest, dirs_exist_ok=True))


def get_directory_size(directory: StrPath) -> int:
    """Total size in bytes of all files under ``directory``."""
    return sum(p.stat().st_size for p in list_files(directory))


def sync_directories(src: StrPath, dest: StrPath) -> list[Path]:
    """One-way sync: copy files from ``src`` that are missing or newer in ``dest``.

    Nothing is deleted from ``dest``.

    Returns:
        The destination paths that were written.
    """
    source = Path(src)
    target = Path(dest)
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for d in list_dirs(source):
        (target / d.relative_to(source)).mkdir(parents=True, exist_ok=True)
    for f in list_files(source):
        out = target / f.relative_to(source)
        if not out.exists() or f.stat().st_mtime > out.stat().st_mtime:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
            written.append(out)
    return written
