"""Convert audio and image files between formats, by extension.

One function, :func:`convert`, dispatches on the kind of the source and
destination: audio goes through pydub (which shells out to ffmpeg for
anything but WAV), images through Pillow. Each backend is an optional extra:

    pip install "novus-pytils[audio]"   # pydub
    pip install "novus-pytils[image]"   # Pillow
    pip install "novus-pytils[all]"

Example:
    >>> from novus_pytils.convert import convert
    >>> convert("song.flac", "song.mp3", bitrate="192k")
    >>> convert("photo.png", "photo.jpg", quality=85)
"""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from novus_pytils.exceptions import ConversionError, MissingDependencyError, UnsupportedFormatError
from novus_pytils.formats import kind_of

# pydub export format names where they differ from the extension.
_AUDIO_FORMATS = {".m4a": "ipod", ".aiff": "aiff", ".opus": "opus"}
# Pillow format names where they differ from the upper-cased extension.
_IMAGE_FORMATS = {".jpg": "JPEG", ".tif": "TIFF"}
# Pillow formats with no alpha channel: drop it rather than fail.
_NO_ALPHA = {"JPEG", "BMP"}


def convert(src: str | PathLike[str], dest: str | PathLike[str], **options: object) -> Path:
    """Convert ``src`` to the format implied by ``dest``'s extension.

    Args:
        src: An audio or image file.
        dest: Where to write; its extension picks the output format and must be
            the same kind (audio to audio, image to image). Parent directories
            are created.
        **options: Passed to the backend. Audio: ``bitrate`` (``"192k"``),
            ``channels`` (1 or 2), ``sample_rate`` (Hz). Image: ``quality``
            (1-100), plus anything Pillow's ``save`` accepts.

    Returns:
        The written path.

    Raises:
        FileNotFoundError: If ``src`` does not exist.
        UnsupportedFormatError: If either side is not audio or image, or the
            kinds differ.
        MissingDependencyError: If the backend extra is not installed.
        ConversionError: If the backend fails.
    """
    source = Path(src)
    target = Path(dest)
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")
    src_kind, dest_kind = kind_of(source), kind_of(target)
    if src_kind not in ("audio", "image"):
        raise UnsupportedFormatError(f"Cannot convert from {source.suffix or 'no extension'!r}")
    if dest_kind != src_kind:
        raise UnsupportedFormatError(
            f"Cannot convert {src_kind} {source.suffix!r} to {target.suffix or 'no extension'!r}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    if src_kind == "audio":
        _convert_audio(source, target, **options)
    else:
        _convert_image(source, target, **options)
    return target


def _convert_audio(
    source: Path,
    target: Path,
    bitrate: str | None = None,
    channels: int | None = None,
    sample_rate: int | None = None,
    **export_options: object,
) -> None:
    try:
        from pydub import AudioSegment
    except ImportError as e:
        raise MissingDependencyError(
            "audio conversion needs pydub: pip install 'novus-pytils[audio]'"
        ) from e
    ext = target.suffix.lower()
    fmt = _AUDIO_FORMATS.get(ext, ext.lstrip("."))
    try:
        audio = AudioSegment.from_file(str(source))
        if channels is not None:
            audio = audio.set_channels(channels)
        if sample_rate is not None:
            audio = audio.set_frame_rate(sample_rate)
        if bitrate is not None and fmt not in ("wav", "flac", "aiff"):
            export_options["bitrate"] = bitrate
        audio.export(str(target), format=fmt, **export_options)
    except Exception as e:
        raise ConversionError(f"Failed to convert {source.name} to {ext}: {e}") from e


def _convert_image(source: Path, target: Path, **save_options: object) -> None:
    try:
        from PIL import Image
    except ImportError as e:
        raise MissingDependencyError(
            "image conversion needs Pillow: pip install 'novus-pytils[image]'"
        ) from e
    ext = target.suffix.lower()
    fmt = _IMAGE_FORMATS.get(ext, ext.lstrip(".").upper())
    try:
        with Image.open(source) as image:
            if fmt in _NO_ALPHA and image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            image.save(target, format=fmt, **save_options)
    except Exception as e:
        raise ConversionError(f"Failed to convert {source.name} to {ext}: {e}") from e
