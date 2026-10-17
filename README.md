# novus-pytils

[![PyPI version](https://img.shields.io/pypi/v/novus-pytils.svg)](https://pypi.org/project/novus-pytils/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jmcmeen/novus-pytils/blob/main/LICENSE)
[![CI](https://github.com/jmcmeen/novus-pytils/actions/workflows/ci.yml/badge.svg)](https://github.com/jmcmeen/novus-pytils/actions/workflows/ci.yml)

Small, dependable helpers for the things scripts do over and over: find and
move files, zip and unzip, load a config, hash a download, print a table.
Nine flat modules, no classes to learn, `pathlib` in and `Path` out.

```sh
pip install novus-pytils
pip install "novus-pytils[all]"   # adds audio (pydub) and image (Pillow) conversion
```

## What's in it

| Module | For |
| --- | --- |
| `files` | read, write, copy, move, back up, find, filter, and sync files and directories |
| `formats` | which kind a file is (audio, image, video, text, archive) and listing by kind |
| `convert` | audio and image format conversion by extension |
| `archive` | zip archives: create, inspect, extract, add, remove |
| `config` | YAML and JSON config files, dotted-key access, layered merging |
| `lists` | flatten, chunk, group, partition, order-preserving set operations, statistics |
| `hashing` | file and text digests, verify a download |
| `validation` | path safety, filename sanitising, sizes, URLs, emails, JSON shape |
| `console` | coloured status lines, tables, a progress bar, prompts |

## A taste

```python
from pathlib import Path
from novus_pytils import files, formats, archive, config, hashing, console

# Every WAV under a folder, newest first, over 1 MB
wavs = formats.get_files("recordings", kind="audio", recursive=True)
big = files.filter_files_by_size(wavs, min_size=1 << 20)

# Pack them up and check the archive
z = archive.create_zip("out/big.zip", big)
console.print_success(f"{archive.zip_info(z).file_count} files, {z.stat().st_size:,} bytes")

# Layered config with dotted keys
cfg = config.merge_configs(config.load_config("defaults.yaml"), config.load_config("local.yaml"))
port = config.get_value(cfg, "database.port", default=5432)

# Verify a download
files.download_file("https://example.org/data.csv", "data.csv")
assert hashing.verify_file("data.csv", "9f86d081...")
```

Every function takes `str` or `Path` and returns `Path` objects for anything
path-like. For what a `Path` already does well (`suffix`, `stem`, `parent`,
`stat()`, `rename()`), use the `Path`.

## Conversion

```python
from novus_pytils.convert import convert

convert("song.flac", "song.mp3", bitrate="192k")   # pydub; ffmpeg for non-WAV
convert("photo.png", "photo.jpg", quality=85)      # Pillow; alpha dropped for JPEG
```

Audio and image conversion are optional extras so the core stays light.
A missing backend raises `MissingDependencyError` with the install hint.

## Development

```sh
make install   # create .venv with dev tooling
make check     # lint, format check, tests
```

## History

Versions 0.0.1 through 0.0.64 were one-function-per-format wrappers over
pydub and Pillow. 0.1.0 is a rewrite around the generic helpers that had
accumulated underneath, with `pathlib`, type hints, and a test for every
function. The old per-format functions are gone; `formats.get_files` and
`convert.convert` replace them.

## License

MIT. See [LICENSE](LICENSE).
