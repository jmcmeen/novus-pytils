# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-17

Versions before 0.1.0 predate this file.

### Changed

- **Rewrite as a small, flat utility package.** The one-function-per-format audio, image,
  video, and text modules are gone, along with the pandas helpers. What remains is the
  generic layer, reorganised into nine modules: `files`, `formats`, `convert`, `archive`,
  `config`, `lists`, `hashing`, `validation`, `console`. Every function takes `str` or
  `Path` and returns `Path` objects, has type hints, and has tests. This is a breaking
  change; see the README for the new names.
- `formats.get_files(directory, kind=..., extensions=...)` replaces the `get_<ext>_files`
  family; `convert.convert(src, dest)` replaces the `<a>_to_<b>` family.
- `pydub` and `Pillow` are now optional extras (`novus-pytils[audio]`, `[image]`, `[all]`);
  the core depends only on `pyyaml` and `requests`.
- Versions come from git tags (hatch-vcs) and releases are cut automatically on merge.
- Requires Python 3.10 or newer.

### Fixed

- `check_disk_space` compared megabytes against kilobytes; it now takes bytes.
- `sanitize_filename` no longer lets `..` through.
- `download_file` streams to disk and raises on HTTP errors instead of writing the error page.

