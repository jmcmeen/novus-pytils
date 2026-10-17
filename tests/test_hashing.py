"""Tests for novus_pytils.hashing."""

from pathlib import Path

import pytest

from novus_pytils import hashing

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"
HELLO_SHA256 = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_text() -> None:
    assert hashing.hash_text("") == EMPTY_SHA256
    assert hashing.hash_text("", "md5") == EMPTY_MD5
    assert hashing.hash_text("hello") == HELLO_SHA256
    assert hashing.hash_text("hello", "md5") == "5d41402abc4b2a76b9719d911017c592"
    assert len(hashing.hash_text("héllo 世界", "blake2b")) == 128


def test_hash_file_matches_text(tmp_path: Path) -> None:
    p = tmp_path / "f"
    p.write_text("hello")
    assert hashing.hash_file(p) == HELLO_SHA256
    p.write_bytes(b"")
    assert hashing.hash_file(p, "md5") == EMPTY_MD5
    big = tmp_path / "big"
    big.write_bytes(b"x" * (3 * (1 << 20) + 17))  # several chunks
    assert hashing.hash_file(big) == hashing.hash_text("x" * (3 * (1 << 20) + 17))
    with pytest.raises(FileNotFoundError):
        hashing.hash_file(tmp_path / "missing")


def test_verify_file(tmp_path: Path) -> None:
    p = tmp_path / "f"
    p.write_text("hello")
    assert hashing.verify_file(p, HELLO_SHA256.upper())
    assert hashing.verify_file(p, " 5d41402abc4b2a76b9719d911017c592\n", "md5")
    assert not hashing.verify_file(p, EMPTY_SHA256)


def test_unknown_algorithm() -> None:
    with pytest.raises(ValueError):
        hashing.hash_text("x", "nope")
