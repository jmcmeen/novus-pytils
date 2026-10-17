"""Small, dependable helpers for files, archives, config, lists, and the console.

Each module is a flat collection of functions with no state. Import the one
you need:

    >>> from novus_pytils import files, archive, config, lists, hashing
    >>> from novus_pytils.files import get_files_by_extension

Modules:
    files       read, write, copy, move, find, sync files and directories
    formats     file-kind registry (audio, image, video, text, archive) and lookup
    convert     audio and image format conversion (needs the ``audio``/``image`` extras)
    archive     zip archives: create, list, extract, add, remove
    config      YAML/JSON config files, dotted-key access, merging
    lists       list helpers: flatten, chunk, group, partition, set operations
    hashing     file and text digests
    validation  path safety, filenames, sizes, URLs, emails, JSON shape
    console     coloured output, tables, a progress bar, prompts
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("novus-pytils")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "archive",
    "config",
    "console",
    "convert",
    "files",
    "formats",
    "hashing",
    "lists",
    "validation",
]
