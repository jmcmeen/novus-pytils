"""Tests for novus_pytils.archive."""

import zipfile
from pathlib import Path

import pytest

from novus_pytils import archive


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    (src / "docs").mkdir(parents=True)
    (src / "a.txt").write_text("alpha")
    (src / "docs" / "b.md").write_text("# beta")
    (src / "docs" / "c.txt").write_text("gamma gamma gamma gamma")
    return src


class TestCreate:
    def test_create_zip_from_files_and_dirs(self, tree: Path, tmp_path: Path) -> None:
        out = archive.create_zip(tmp_path / "out" / "x.zip", [tree / "a.txt", tree / "docs"])
        assert out.is_file()
        assert archive.list_zip(out) == ["a.txt", "docs/b.md", "docs/c.txt"]

    def test_create_zip_with_arcnames(self, tree: Path, tmp_path: Path) -> None:
        out = archive.create_zip(
            tmp_path / "x.zip", {tree / "a.txt": "renamed/a.txt", tree / "docs": "d"}
        )
        assert archive.list_zip(out) == ["renamed/a.txt", "d/b.md", "d/c.txt"]

    def test_create_zip_missing_source(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            archive.create_zip(tmp_path / "x.zip", [tmp_path / "nope"])

    def test_zip_directory_contents_at_root(self, tree: Path) -> None:
        out = archive.zip_directory(tree)
        assert out == tree.with_suffix(".zip")
        assert archive.list_zip(out) == ["a.txt", "docs/b.md", "docs/c.txt"]
        with pytest.raises(NotADirectoryError):
            archive.zip_directory(tree / "a.txt")


class TestInspect:
    def test_zip_info_and_validity(self, tree: Path, tmp_path: Path) -> None:
        out = archive.zip_directory(tree, tmp_path / "t.zip")
        info = archive.zip_info(out)
        assert info.path == out and info.file_count == 3
        assert info.total_size == 5 + 6 + 23
        assert info.members == ("a.txt", "docs/b.md", "docs/c.txt")
        assert 0.0 <= info.compression_ratio < 1.0
        assert archive.is_valid_zip(out)
        assert not archive.is_valid_zip(tree / "a.txt")
        assert not archive.is_valid_zip(tmp_path / "missing.zip")
        corrupt = tmp_path / "bad.zip"
        corrupt.write_bytes(out.read_bytes()[:-30] + b"\x00" * 30)
        assert not archive.is_valid_zip(corrupt)

    def test_empty_archive_ratio(self, tmp_path: Path) -> None:
        with zipfile.ZipFile(tmp_path / "e.zip", "w"):
            pass
        assert archive.zip_info(tmp_path / "e.zip").compression_ratio == 0.0


class TestExtract:
    def test_extract_all_members_and_pattern(self, tree: Path, tmp_path: Path) -> None:
        z = archive.zip_directory(tree, tmp_path / "t.zip")
        got = archive.extract_zip(z, tmp_path / "all")
        assert [p.relative_to(tmp_path / "all").as_posix() for p in got] == [
            "a.txt",
            "docs/b.md",
            "docs/c.txt",
        ]
        assert (tmp_path / "all" / "docs" / "b.md").read_text() == "# beta"

        some = archive.extract_zip(z, tmp_path / "some", members=["docs/c.txt"])
        assert some == [tmp_path / "some" / "docs" / "c.txt"]
        assert not (tmp_path / "some" / "a.txt").exists()

        txt = archive.extract_zip(z, tmp_path / "txt", pattern="*.txt")
        assert [p.name for p in txt] == ["a.txt", "c.txt"]

        with pytest.raises(KeyError):
            archive.extract_zip(z, tmp_path / "x", members=["nope"])


class TestModify:
    def test_add_and_remove(self, tree: Path, tmp_path: Path) -> None:
        z = archive.create_zip(tmp_path / "t.zip", [tree / "a.txt"])
        extra = tmp_path / "extra.txt"
        extra.write_text("extra")
        archive.add_to_zip(z, [extra])
        archive.add_to_zip(z, {tree / "docs": "docs"})
        assert archive.list_zip(z) == ["a.txt", "extra.txt", "docs/b.md", "docs/c.txt"]

        assert archive.remove_from_zip(z, members=["extra.txt"]) == ["extra.txt"]
        assert archive.remove_from_zip(z, pattern="docs/*") == ["docs/b.md", "docs/c.txt"]
        assert archive.remove_from_zip(z, members=["nope"]) == []
        assert archive.list_zip(z) == ["a.txt"]
        assert archive.is_valid_zip(z)
        with zipfile.ZipFile(z) as zf:
            assert zf.read("a.txt") == b"alpha"
