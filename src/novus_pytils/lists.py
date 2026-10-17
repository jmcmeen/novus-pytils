"""List helpers that the standard library makes you write every time."""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable
from os import PathLike
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


def read_lines(
    path: str | PathLike[str], encoding: str = "utf-8", keep_empty: bool = True
) -> list[str]:
    """Lines of a text file with surrounding whitespace stripped."""
    lines = [line.strip() for line in Path(path).read_text(encoding=encoding).splitlines()]
    return lines if keep_empty else [line for line in lines if line]


def write_lines(path: str | PathLike[str], lines: Iterable[Any], encoding: str = "utf-8") -> Path:
    """Write items one per line (``str()`` applied), creating parent directories."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(f"{line}\n" for line in lines), encoding=encoding)
    return target


def flatten_list(nested: Iterable[Any]) -> list[Any]:
    """Flatten nested lists and tuples to one level, in order."""
    flat: list[Any] = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat


def remove_duplicates(items: Iterable[K]) -> list[K]:
    """Unique items, first occurrence wins, order kept."""
    return list(dict.fromkeys(items))


def chunk_list(items: list[T], size: int) -> list[list[T]]:
    """Split into consecutive chunks of ``size``; the last may be shorter.

    Raises:
        ValueError: If ``size`` is less than 1.
    """
    if size < 1:
        raise ValueError(f"size must be at least 1, got {size}")
    return [items[i : i + size] for i in range(0, len(items), size)]


def find_in_list(
    items: Iterable[T], predicate: Callable[[T], bool], default: T | None = None
) -> T | None:
    """The first item for which ``predicate`` is true, else ``default``."""
    return next((item for item in items if predicate(item)), default)


def partition_list(items: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """Split into ``(matching, not_matching)`` by ``predicate``, order kept."""
    yes: list[T] = []
    no: list[T] = []
    for item in items:
        (yes if predicate(item) else no).append(item)
    return yes, no


def sort_list_of_dicts(
    items: list[dict[str, Any]], key: str, reverse: bool = False
) -> list[dict[str, Any]]:
    """Sort dicts by one key.

    Raises:
        KeyError: If any dict lacks ``key``.
    """
    for item in items:
        if key not in item:
            raise KeyError(f"Key {key!r} missing from {item!r}")
    return sorted(items, key=lambda d: d[key], reverse=reverse)


def group_by_key(items: Iterable[dict[str, Any]], key: str) -> dict[Any, list[dict[str, Any]]]:
    """Group dicts by the value of one key, in first-seen order.

    Raises:
        KeyError: If any dict lacks ``key``.
    """
    groups: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        if key not in item:
            raise KeyError(f"Key {key!r} missing from {item!r}")
        groups[item[key]].append(item)
    return dict(groups)


def list_intersection(a: Iterable[K], b: Iterable[K]) -> list[K]:
    """Items in both, in ``a``'s order, without duplicates."""
    present = set(b)
    return [item for item in remove_duplicates(a) if item in present]


def list_union(a: Iterable[K], b: Iterable[K]) -> list[K]:
    """Items in either, ``a``'s first, without duplicates."""
    return remove_duplicates([*a, *b])


def list_difference(a: Iterable[K], b: Iterable[K]) -> list[K]:
    """Items in ``a`` but not ``b``, in ``a``'s order, without duplicates."""
    absent = set(b)
    return [item for item in remove_duplicates(a) if item not in absent]


def rotate_list(items: list[T], positions: int) -> list[T]:
    """Rotate right by ``positions`` (negative rotates left)."""
    if not items:
        return []
    positions %= len(items)
    return items[-positions:] + items[:-positions] if positions else list(items)


def merge_sorted_lists(a: Iterable[T], b: Iterable[T]) -> list[T]:
    """Merge two already-sorted iterables into one sorted list."""
    import heapq

    return list(heapq.merge(a, b))


def get_list_statistics(values: Iterable[float]) -> dict[str, float | None]:
    """count, sum, min, max, mean, median, stdev (sample; 0.0 for a single value).

    An empty input gives count 0, sum 0, and ``None`` for the rest.
    """
    data = list(values)
    if not data:
        return {
            "count": 0,
            "sum": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "stdev": None,
        }
    return {
        "count": len(data),
        "sum": sum(data),
        "min": min(data),
        "max": max(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "stdev": statistics.stdev(data) if len(data) > 1 else 0.0,
    }
