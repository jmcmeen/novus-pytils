"""Tests for novus_pytils.formats."""

from pathlib import Path

import pytest

from novus_pytils import formats


def test_registry_is_disjoint_and_lowercase() -> None:
    seen: set[str] = set()
    for kind, exts in formats.KINDS.items():
        assert kind in ("audio", "image", "video", "text", "archive")
        for e in exts:
            assert e.startswith(".") and e == e.lower()
            assert e not in seen, f"{e} registered twice"
            seen.add(e)


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("song.MP3", "audio"),
        ("photo.jpeg", "image"),
        ("clip.mkv", "video"),
        ("notes.md", "text"),
        ("bundle.tar.gz", "archive"),
        ("Makefile", None),
        ("weird.xyz", None),
    ],
)
def test_kind_of(name: str, kind: str | None) -> None:
    assert formats.kind_of(name) == kind
    assert formats.kind_of(Path("/x") / name) == kind


def test_is_kind_and_extensions_for() -> None:
    assert formats.is_kind("a.WAV", "audio")
    assert not formats.is_kind("a.wav", "image")
    assert ".png" in formats.extensions_for("image")
    with pytest.raises(KeyError):
        formats.extensions_for("spreadsheet")


def test_get_files(tmp_path: Path) -> None:
    for name in ("a.wav", "b.MP3", "c.png", "d.txt", "e.zip"):
        (tmp_path / name).write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "f.flac").write_bytes(b"x")

    assert [p.name for p in formats.get_files(tmp_path, kind="audio")] == ["a.wav", "b.MP3"]
    assert [p.name for p in formats.get_files(tmp_path, kind="audio", recursive=True)] == [
        "a.wav",
        "b.MP3",
        "f.flac",
    ]
    assert [p.name for p in formats.get_files(tmp_path, extensions="txt")] == ["d.txt"]
    assert [p.name for p in formats.get_files(tmp_path, kind="image", extensions=[".zip"])] == [
        "c.png",
        "e.zip",
    ]
    assert len(formats.get_files(tmp_path)) == 5
    assert formats.get_files(tmp_path / "missing", kind="audio") == []
