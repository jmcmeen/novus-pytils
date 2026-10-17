"""Zip archives: create, inspect, extract, add to, and remove from.

Archive member names always use forward slashes, whatever the platform.
"""

from __future__ import annotations

import fnmatch
import shutil
import tempfile
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

StrPath = str | PathLike[str]


@dataclass(frozen=True)
class ZipInfo:
    """Summary of an archive, from :func:`zip_info`.

    Attributes:
        path: The archive.
        members: Member names, directories included, in archive order.
        file_count: Number of file members (directories excluded).
        total_size: Uncompressed bytes of all file members.
        compressed_size: Compressed bytes of all file members.
    """

    path: Path
    members: tuple[str, ...]
    file_count: int
    total_size: int
    compressed_size: int

    @property
    def compression_ratio(self) -> float:
        """Fraction of space saved, 0.0 for an empty archive."""
        if self.total_size == 0:
            return 0.0
        return 1 - self.compressed_size / self.total_size


def is_valid_zip(path: StrPath) -> bool:
    """True if ``path`` is a zip archive whose members pass a CRC check."""
    target = Path(path)
    if not target.is_file() or not zipfile.is_zipfile(target):
        return False
    try:
        with zipfile.ZipFile(target) as zf:
            return zf.testzip() is None
    except zipfile.BadZipFile:
        return False


def list_zip(path: StrPath) -> list[str]:
    """Member names in archive order."""
    with zipfile.ZipFile(path) as zf:
        return zf.namelist()


def zip_info(path: StrPath) -> ZipInfo:
    """Summarise an archive without extracting it."""
    target = Path(path)
    with zipfile.ZipFile(target) as zf:
        infos = zf.infolist()
    files = [i for i in infos if not i.is_dir()]
    return ZipInfo(
        path=target,
        members=tuple(i.filename for i in infos),
        file_count=len(files),
        total_size=sum(i.file_size for i in files),
        compressed_size=sum(i.compress_size for i in files),
    )


def _add_path(zf: zipfile.ZipFile, source: Path, arcname: str) -> None:
    """Write a file, or a directory tree, under ``arcname``."""
    if source.is_dir():
        for child in sorted(source.rglob("*")):
            if child.is_file():
                rel = child.relative_to(source).as_posix()
                zf.write(child, f"{arcname}/{rel}" if arcname else rel)
    else:
        zf.write(source, arcname)


def create_zip(
    path: StrPath,
    files: Iterable[StrPath] | Mapping[StrPath, str],
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    """Create (or replace) an archive from files and directories.

    Args:
        path: The archive to write; parents are created.
        files: Paths to add, each stored under its own name; or a mapping of
            path to the name it should have in the archive. A directory adds
            its whole tree.
        compression: A :mod:`zipfile` constant.

    Returns:
        The archive's path.

    Raises:
        FileNotFoundError: If any source is missing.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    items = files.items() if isinstance(files, Mapping) else ((f, Path(f).name) for f in files)
    with zipfile.ZipFile(target, "w", compression=compression) as zf:
        for src, arcname in items:
            source = Path(src)
            if not source.exists():
                raise FileNotFoundError(f"Cannot add missing path to archive: {source}")
            _add_path(zf, source, arcname)
    return target


def zip_directory(
    directory: StrPath, path: StrPath | None = None, compression: int = zipfile.ZIP_DEFLATED
) -> Path:
    """Archive a directory's contents (not the directory itself as a top-level folder).

    Args:
        directory: The directory to archive.
        path: The archive to write. Defaults to ``<directory>.zip`` beside it.
    """
    source = Path(directory)
    if not source.is_dir():
        raise NotADirectoryError(f"Not a directory: {source}")
    target = Path(path) if path is not None else source.with_suffix(".zip")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=compression) as zf:
        _add_path(zf, source, "")
    return target


def extract_zip(
    path: StrPath, to: StrPath, members: Iterable[str] | None = None, pattern: str | None = None
) -> list[Path]:
    """Extract an archive, or part of one, into a directory.

    Args:
        path: The archive.
        to: Destination directory; created if missing.
        members: Exact member names to extract. Default: all.
        pattern: A shell-style wildcard (``*.txt``, ``docs/*``) members must match.

    Returns:
        The paths written, in archive order.

    Raises:
        KeyError: If a name in ``members`` is not in the archive.
    """
    dest = Path(to)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if members is not None:
            wanted = list(members)
            missing = [m for m in wanted if m not in names]
            if missing:
                raise KeyError(f"Not in archive: {missing}")
            names = [n for n in names if n in set(wanted)]
        if pattern is not None:
            names = [n for n in names if fnmatch.fnmatch(n, pattern)]
        zf.extractall(dest, members=names)
    return [dest / n for n in names if not n.endswith("/")]


def add_to_zip(path: StrPath, files: Iterable[StrPath] | Mapping[StrPath, str]) -> Path:
    """Append files or directory trees to an existing archive (see :func:`create_zip` for ``files``)."""
    target = Path(path)
    items = files.items() if isinstance(files, Mapping) else ((f, Path(f).name) for f in files)
    with zipfile.ZipFile(target, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in items:
            source = Path(src)
            if not source.exists():
                raise FileNotFoundError(f"Cannot add missing path to archive: {source}")
            _add_path(zf, source, arcname)
    return target


def remove_from_zip(
    path: StrPath, members: Iterable[str] | None = None, pattern: str | None = None
) -> list[str]:
    """Remove members by exact name or by wildcard, rewriting the archive.

    Returns:
        The names removed.
    """
    target = Path(path)
    wanted = set(members or ())
    with zipfile.ZipFile(target) as zf:
        infos = zf.infolist()
        drop = [
            i.filename
            for i in infos
            if i.filename in wanted
            or (pattern is not None and fnmatch.fnmatch(i.filename, pattern))
        ]
        if not drop:
            return []
        keep = [i for i in infos if i.filename not in set(drop)]
        tmp = Path(tempfile.mkstemp(suffix=".zip", dir=target.parent)[1])
        try:
            with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as out:
                for info in keep:
                    out.writestr(info, zf.read(info.filename))
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    shutil.move(str(tmp), str(target))
    return drop
