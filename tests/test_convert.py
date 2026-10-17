"""Tests for novus_pytils.convert.

Image conversion runs for real through Pillow. Audio conversion between
compressed formats needs ffmpeg, so the real audio test only does WAV to WAV,
which pydub handles natively, and the rest is checked through a fake backend.
"""

import struct
import sys
import wave
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from novus_pytils.convert import convert
from novus_pytils.exceptions import ConversionError, MissingDependencyError, UnsupportedFormatError


def _wav(path: Path, seconds: float = 0.1, rate: int = 8000) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", 0) for _ in range(int(rate * seconds))))
    return path


def _png(path: Path) -> Path:
    PIL = pytest.importorskip("PIL.Image")
    PIL.new("RGBA", (4, 3), (255, 0, 0, 128)).save(path)
    return path


class TestDispatch:
    def test_missing_source(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            convert(tmp_path / "nope.wav", tmp_path / "out.mp3")

    def test_unsupported_source_kind(self, tmp_path: Path) -> None:
        src = tmp_path / "doc.txt"
        src.write_text("x")
        with pytest.raises(UnsupportedFormatError, match="from"):
            convert(src, tmp_path / "doc.pdf")

    def test_kinds_must_match(self, tmp_path: Path) -> None:
        src = _wav(tmp_path / "a.wav")
        with pytest.raises(UnsupportedFormatError, match="audio"):
            convert(src, tmp_path / "a.png")
        with pytest.raises(UnsupportedFormatError):
            convert(src, tmp_path / "a")


class TestImage:
    def test_png_to_jpg_drops_alpha_and_creates_parents(self, tmp_path: Path) -> None:
        from PIL import Image

        src = _png(tmp_path / "in.png")
        out = convert(src, tmp_path / "out" / "photo.jpg", quality=70)
        assert out == tmp_path / "out" / "photo.jpg"
        with Image.open(out) as im:
            assert im.format == "JPEG" and im.mode == "RGB" and im.size == (4, 3)

    def test_png_to_webp_keeps_alpha(self, tmp_path: Path) -> None:
        from PIL import Image

        out = convert(_png(tmp_path / "in.png"), tmp_path / "out.webp")
        with Image.open(out) as im:
            assert im.format == "WEBP" and "A" in im.mode

    def test_backend_failure_is_conversion_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.png"
        bad.write_bytes(b"not an image")
        with pytest.raises(ConversionError):
            convert(bad, tmp_path / "out.jpg")


class TestAudio:
    def test_wav_to_wav_with_resample(self, tmp_path: Path) -> None:
        pytest.importorskip("pydub")
        src = _wav(tmp_path / "in.wav", rate=8000)
        out = convert(src, tmp_path / "out.wav", sample_rate=16000, channels=2)
        with wave.open(str(out)) as w:
            assert w.getframerate() == 16000 and w.getnchannels() == 2

    def test_options_reach_pydub(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """A fake pydub shows which export format and options each extension gets."""
        segment = MagicMock()
        segment.set_channels.return_value = segment
        segment.set_frame_rate.return_value = segment
        fake = ModuleType("pydub")
        fake.AudioSegment = MagicMock()
        fake.AudioSegment.from_file.return_value = segment
        monkeypatch.setitem(sys.modules, "pydub", fake)
        src = _wav(tmp_path / "in.wav")

        convert(src, tmp_path / "out.m4a", bitrate="128k", channels=1)
        segment.set_channels.assert_called_once_with(1)
        segment.export.assert_called_once_with(
            str(tmp_path / "out.m4a"), format="ipod", bitrate="128k"
        )

        segment.export.reset_mock()
        convert(src, tmp_path / "out.flac", bitrate="128k")  # lossless: bitrate dropped
        segment.export.assert_called_once_with(str(tmp_path / "out.flac"), format="flac")

    def test_missing_pydub(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "pydub", None)  # makes `import pydub` fail
        with pytest.raises(MissingDependencyError, match="novus-pytils\\[audio\\]"):
            convert(_wav(tmp_path / "in.wav"), tmp_path / "out.mp3")
