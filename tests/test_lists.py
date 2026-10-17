"""Tests for novus_pytils.lists."""

from pathlib import Path

import pytest

from novus_pytils import lists


def test_read_and_write_lines(tmp_path: Path) -> None:
    p = lists.write_lines(tmp_path / "d" / "f.txt", ["a", 1, " b "])
    assert p.read_text() == "a\n1\n b \n"
    assert lists.read_lines(p) == ["a", "1", "b"]
    p.write_text("x\n\ny\n")
    assert lists.read_lines(p) == ["x", "", "y"]
    assert lists.read_lines(p, keep_empty=False) == ["x", "y"]
    assert lists.read_lines(lists.write_lines(tmp_path / "e", [])) == []


def test_flatten_list() -> None:
    assert lists.flatten_list([1, [2, (3, [4])], 5]) == [1, 2, 3, 4, 5]
    assert lists.flatten_list([]) == []
    assert lists.flatten_list(["ab", ["cd"]]) == ["ab", "cd"]  # strings are not split


def test_remove_duplicates_keeps_first_order() -> None:
    assert lists.remove_duplicates([3, 1, 2, 1, 3]) == [3, 1, 2]
    assert lists.remove_duplicates("abca") == ["a", "b", "c"]


def test_chunk_list() -> None:
    assert lists.chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert lists.chunk_list([], 3) == []
    with pytest.raises(ValueError):
        lists.chunk_list([1], 0)


def test_find_and_partition() -> None:
    assert lists.find_in_list([1, 2, 3, 4], lambda x: x % 2 == 0) == 2
    assert lists.find_in_list([1, 3], lambda x: x > 5) is None
    assert lists.find_in_list([], lambda x: True, default="none") == "none"
    assert lists.partition_list(range(6), lambda x: x % 2 == 0) == ([0, 2, 4], [1, 3, 5])


def test_dict_helpers() -> None:
    people = [{"n": "c", "a": 3}, {"n": "a", "a": 1}, {"n": "b", "a": 1}]
    assert [d["n"] for d in lists.sort_list_of_dicts(people, "n")] == ["a", "b", "c"]
    assert [d["n"] for d in lists.sort_list_of_dicts(people, "a", reverse=True)] == ["c", "a", "b"]
    assert list(lists.group_by_key(people, "a")) == [3, 1]
    assert len(lists.group_by_key(people, "a")[1]) == 2
    with pytest.raises(KeyError):
        lists.sort_list_of_dicts(people + [{"n": "x"}], "a")
    with pytest.raises(KeyError):
        lists.group_by_key([{"n": "x"}], "a")


def test_set_operations_keep_order() -> None:
    assert lists.list_intersection([3, 1, 2, 1], [2, 3, 9]) == [3, 2]
    assert lists.list_union([1, 2, 2], [3, 1]) == [1, 2, 3]
    assert lists.list_difference([1, 2, 3, 2], [2]) == [1, 3]
    assert lists.list_intersection([], [1]) == []


def test_rotate_list() -> None:
    assert lists.rotate_list([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert lists.rotate_list([1, 2, 3, 4, 5], -2) == [3, 4, 5, 1, 2]
    assert lists.rotate_list([1, 2, 3], 3) == [1, 2, 3]
    assert lists.rotate_list([1, 2, 3], 4) == [3, 1, 2]
    assert lists.rotate_list([], 7) == []


def test_merge_sorted_lists() -> None:
    assert lists.merge_sorted_lists([1, 3, 5], [2, 4]) == [1, 2, 3, 4, 5]
    assert lists.merge_sorted_lists([], [1]) == [1]
    assert lists.merge_sorted_lists([1, 2], [2, 3]) == [1, 2, 2, 3]


def test_get_list_statistics() -> None:
    s = lists.get_list_statistics([1.0, 2.0, 3.0, 4.0])
    assert s["count"] == 4 and s["sum"] == 10.0 and s["mean"] == 2.5 and s["median"] == 2.5
    assert s["min"] == 1.0 and s["max"] == 4.0 and s["stdev"] == pytest.approx(1.29099, abs=1e-4)
    assert lists.get_list_statistics([7])["stdev"] == 0.0
    empty = lists.get_list_statistics([])
    assert empty["count"] == 0 and empty["sum"] == 0 and empty["mean"] is None
