"""Tests for novus_pytils.files."""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from novus_pytils import files


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A small directory tree: two txt and a md at the top, a txt in a subdir."""
    (tmp_path / "file1.txt").write_text("Content 1")
    (tmp_path / "file2.TXT").write_text("Content 22")
    (tmp_path / "readme.md").write_text("# Test README")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "file3.txt").write_text("Content 333")
    (sub / "deeper").mkdir()
    return tmp_path


class TestSingleFiles:
    def test_read_write_text_and_bytes(self, tmp_path: Path) -> None:
        p = files.write_file(tmp_path / "a" / "b.txt", "hëllo")
        assert p == tmp_path / "a" / "b.txt"
        assert files.read_file_text(p) == "hëllo"
        files.write_file(p, b"\x00\x01")
        assert files.read_file_bytes(str(p)) == b"\x00\x01"

    def test_append_creates_and_extends(self, tmp_path: Path) -> None:
        p = tmp_path / "log.txt"
        files.append_to_file(p, "one\n")
        files.append_to_file(p, "two\n")
        assert p.read_text() == "one\ntwo\n"

    def test_size_and_empty(self, tmp_path: Path) -> None:
        p = files.write_file(tmp_path / "x", "abcd")
        assert files.get_file_size(p) == 4
        assert not files.is_file_empty(p)
        assert files.is_file_empty(files.write_file(tmp_path / "e", ""))
        with pytest.raises(FileNotFoundError):
            files.get_file_size(tmp_path / "missing")

    def test_file_exists_is_false_for_directories(self, tmp_path: Path) -> None:
        assert files.file_exists(files.write_file(tmp_path / "f", "x"))
        assert not files.file_exists(tmp_path)
        assert not files.file_exists(tmp_path / "nope")

    def test_delete_file(self, tmp_path: Path) -> None:
        p = files.write_file(tmp_path / "f", "x")
        assert files.delete_file(p) is True
        assert files.delete_file(p) is False
        with pytest.raises(IsADirectoryError):
            files.delete_file(tmp_path)

    def test_copy_and_move(self, tmp_path: Path) -> None:
        src = files.write_file(tmp_path / "src.txt", "data")
        copied = files.copy_file(src, tmp_path / "out" / "copy.txt")
        assert copied.read_text() == "data" and src.exists()
        moved = files.move_file(copied, tmp_path / "moved.txt")
        assert moved.read_text() == "data" and not copied.exists()
        with pytest.raises(FileNotFoundError):
            files.copy_file(tmp_path / "missing", tmp_path / "x")

    def test_copy_files_enumerates_duplicates(self, tmp_path: Path) -> None:
        a = files.write_file(tmp_path / "a" / "same.txt", "1")
        b = files.write_file(tmp_path / "b" / "same.txt", "2")
        dest = tmp_path / "dest"
        written = files.copy_files([a, b], dest)
        assert [p.name for p in written] == ["same.txt", "same_1.txt"]
        assert (dest / "same_1.txt").read_text() == "2"
        files.copy_files([a], dest, enumerate_dups=False)
        assert (dest / "same.txt").read_text() == "1"

    def test_backup_and_restore(self, tmp_path: Path) -> None:
        p = files.write_file(tmp_path / "conf.ini", "v1")
        bak = files.create_backup(p)
        assert bak == tmp_path / "conf.ini.bak"
        p.write_text("v2")
        assert files.restore_backup(bak) == p
        assert p.read_text() == "v1"
        elsewhere = files.create_backup(p, tmp_path / "backups")
        assert elsewhere == tmp_path / "backups" / "conf.ini.bak"
        with pytest.raises(ValueError):
            files.restore_backup(p)  # not a .bak, no original given

    def test_download_file_streams_and_raises(self, tmp_path: Path) -> None:
        response = MagicMock()
        response.iter_content.return_value = [b"abc", b"def"]
        response.__enter__.return_value = response
        with patch("requests.get", return_value=response) as get:
            out = files.download_file("https://example.com/f", tmp_path / "d" / "f")
            get.assert_called_once_with("https://example.com/f", stream=True, timeout=60.0)
        assert out.read_bytes() == b"abcdef"

        response.raise_for_status.side_effect = RuntimeError("404")
        with patch("requests.get", return_value=response), pytest.raises(RuntimeError):
            files.download_file("https://example.com/f", tmp_path / "g")


class TestFiltering:
    def test_by_size(self, tmp_path: Path) -> None:
        small = files.write_file(tmp_path / "s", "x")
        large = files.write_file(tmp_path / "l", "x" * 1000)
        missing = tmp_path / "missing"
        assert files.filter_files_by_size([small, large, missing], min_size=500) == [large]
        assert files.filter_files_by_size([small, large], max_size=500) == [small]

    def test_by_date(self, tmp_path: Path) -> None:
        old = files.write_file(tmp_path / "old", "x")
        past = time.time() - 86400
        os.utime(old, (past, past))
        new = files.write_file(tmp_path / "new", "x")
        cutoff = datetime.now() - timedelta(hours=1)
        assert files.filter_files_by_date([old, new], after=cutoff) == [new]
        assert files.filter_files_by_date([old, new], before=cutoff) == [old]


class TestFinding:
    def test_list_files_and_dirs(self, tree: Path) -> None:
        assert [p.name for p in files.list_files(tree, recursive=False)] == [
            "file1.txt",
            "file2.TXT",
            "readme.md",
        ]
        assert len(files.list_files(tree)) == 4
        assert [p.name for p in files.list_dirs(tree)] == ["subdir", "deeper"]
        assert files.list_dirs(tree, recursive=False) == [tree / "subdir"]
        assert files.list_files(tree / "missing") == []

    def test_get_files_by_extension(self, tree: Path) -> None:
        top = files.get_files_by_extension(tree, ".txt")
        assert [p.name for p in top] == ["file1.txt", "file2.TXT"]  # case-insensitive
        assert len(files.get_files_by_extension(tree, ["txt", ".md"], recursive=True)) == 4
        assert files.get_files_by_extension(tree, ".xyz") == []

    def test_find_by_substring(self, tree: Path) -> None:
        assert [p.name for p in files.find_files(tree, "FILE")] == [
            "file1.txt",
            "file2.TXT",
            "file3.txt",
        ]
        assert files.find_dirs(tree, "deep") == [tree / "subdir" / "deeper"]
        assert files.directory_contains_file(tree, "readme")
        assert not files.directory_contains_file(tree, "nope")
        assert files.directory_contains_directory(tree, "sub")
        assert files.directory_contains_file_with_extension(tree, "md")
        assert not files.directory_contains_file_with_extension(tree, ".png")

    def test_counts(self, tree: Path) -> None:
        assert files.count_files(tree) == 3
        assert files.count_files(tree, recursive=True) == 4
        assert files.count_files(tree / "missing") == 0
        assert files.get_subdirectories(tree) == [tree / "subdir"]


class TestDirectories:
    def test_create_exists_delete_recreate(self, tmp_path: Path) -> None:
        d = files.create_directory(tmp_path / "a" / "b")
        assert files.directory_exists(d)
        files.create_directory(d)  # idempotent
        files.write_file(d / "f", "x")
        assert files.delete_directory(d) is True
        assert files.delete_directory(d) is False
        assert not files.directory_exists(d)
        files.write_file(tmp_path / "r" / "junk", "x")
        files.recreate_directory(tmp_path / "r")
        assert files.list_files(tmp_path / "r") == []

    def test_copy_directory_and_size(self, tree: Path, tmp_path: Path) -> None:
        dest = files.copy_directory(tree, tmp_path.parent / f"{tmp_path.name}-copy")
        try:
            assert files.count_files(dest, recursive=True) == 4
            assert files.get_directory_size(dest) == 9 + 10 + 13 + 11
            files.copy_directory(tree, dest)  # existing destination is fine
        finally:
            files.delete_directory(dest)

    def test_sync_directories_copies_new_and_newer_only(self, tree: Path, tmp_path: Path) -> None:
        dest = tmp_path.parent / f"{tmp_path.name}-sync"
        try:
            first = files.sync_directories(tree, dest)
            assert len(first) == 4 and (dest / "subdir" / "deeper").is_dir()
            assert files.sync_directories(tree, dest) == []  # nothing newer
            (tree / "file1.txt").write_text("changed")
            future = time.time() + 10
            os.utime(tree / "file1.txt", (future, future))
            assert files.sync_directories(tree, dest) == [dest / "file1.txt"]
            assert (dest / "file1.txt").read_text() == "changed"
        finally:
            files.delete_directory(dest)
