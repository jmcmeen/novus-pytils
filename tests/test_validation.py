"""Tests for novus_pytils.validation."""

from pathlib import Path
from unittest.mock import patch

import pytest

from novus_pytils import validation as v


def test_validation_result_is_truthy_when_valid() -> None:
    assert v.ValidationResult(True, "ok")
    assert not v.ValidationResult(False, "no")
    assert v.ValidationResult(False).errors == []


class TestPaths:
    @pytest.mark.parametrize(
        "path", ["file.txt", "a/b.txt", "./c.txt", "a\\b.txt", "..hidden", "a..b"]
    )
    def test_no_traversal(self, path: str) -> None:
        assert not v.has_path_traversal(path)

    @pytest.mark.parametrize("path", ["../x", "a/../../etc/passwd", "..\\windows", ".."])
    def test_traversal(self, path: str) -> None:
        assert v.has_path_traversal(path)

    def test_dangerous_chars(self) -> None:
        assert not v.contains_dangerous_chars("my-file_1.txt")
        for bad in ("a<b", "a|b", 'a"b', "a?b", "a*b", "a:b", "a\x00b"):
            assert v.contains_dangerous_chars(bad)

    def test_is_safe_path(self, tmp_path: Path) -> None:
        assert v.is_safe_path("docs/readme.md")
        assert not v.is_safe_path("../secret")
        assert not v.is_safe_path("bad|name")
        assert v.is_safe_path(tmp_path / "inside.txt", tmp_path)
        assert not v.is_safe_path(tmp_path.parent / "outside.txt", tmp_path)

    def test_sanitize_filename(self) -> None:
        assert v.sanitize_filename("clean_file.txt") == "clean_file.txt"
        assert v.sanitize_filename('a<b>:"c|d?e*f.txt') == "a_b___c_d_e_f.txt"
        assert ".." not in v.sanitize_filename("../../../etc/passwd")
        assert v.sanitize_filename("  .dots. ") == "dots"
        assert v.sanitize_filename("") == "unnamed"
        assert v.sanitize_filename("///") == "unnamed"
        assert v.sanitize_filename("CON.txt") == "_CON.txt"
        assert v.sanitize_filename("lpt1") == "_lpt1"
        long = v.sanitize_filename("x" * 300 + ".tar")
        assert len(long) == 255 and long.endswith(".tar")

    def test_validate_file_path(self, tmp_path: Path) -> None:
        existing = tmp_path / "f"
        existing.write_text("x")
        assert v.validate_file_path(str(existing))
        assert not v.validate_file_path("")
        assert not v.validate_file_path(None)
        assert "exist" in v.validate_file_path(str(tmp_path / "nope")).message
        assert v.validate_file_path(str(tmp_path / "nope"), must_exist=False)
        assert "'..'" in v.validate_file_path("../x", must_exist=False).message
        assert not v.validate_file_path("a|b", must_exist=False)
        assert not v.validate_file_path("x" * 5000, must_exist=False)


class TestFiles:
    def test_validate_file_extension(self) -> None:
        assert v.validate_file_extension("a.TXT", ["txt", ".md"])
        assert "not allowed" in v.validate_file_extension("a.pdf", ["txt"]).message
        assert "no extension" in v.validate_file_extension("Makefile", ["txt"]).message

    def test_validate_file_size(self, tmp_path: Path) -> None:
        p = tmp_path / "f"
        p.write_bytes(b"x" * 100)
        assert v.validate_file_size(p, max_bytes=100)
        assert "larger" in v.validate_file_size(p, max_bytes=99).message
        assert "smaller" in v.validate_file_size(p, min_bytes=101).message
        assert not v.validate_file_size(tmp_path / "nope")

    def test_check_disk_space(self, tmp_path: Path) -> None:
        assert v.check_disk_space(tmp_path, 1)
        with patch("shutil.disk_usage") as usage:
            usage.return_value = (10, 9, 1 << 20)
            assert v.check_disk_space(tmp_path, 1 << 20)
            assert "Insufficient" in v.check_disk_space(tmp_path, (1 << 20) + 1).message
        assert not v.check_disk_space(tmp_path / "missing" / "deeper", 1)


class TestText:
    def test_validate_url(self) -> None:
        for url in ("https://example.com", "http://t.org/p?q=1", "https://sub.d.com:8080/x"):
            assert v.validate_url(url)
        for url in ("not-a-url", "ftp://example.com", "https://", ""):
            assert not v.validate_url(url)
        assert v.validate_url("ftp://example.com", schemes=["ftp"])

    def test_validate_email(self) -> None:
        for e in ("test@example.com", "user.name@domain.org", "user+tag@domain.co.uk"):
            assert v.validate_email(e)
        for e in ("invalid", "@domain.com", "user@", "user@domain", "", "a@b..com"):
            assert not v.validate_email(e)

    def test_validate_json_structure(self) -> None:
        assert v.validate_json_structure({"name": "t", "n": 1}, required=["name", "n"])
        r = v.validate_json_structure('{"name": "t"}', required=["name", "n"], types={"name": int})
        assert not r and r.errors == [
            "Missing required key: n",
            "Key 'name' should be int, got str",
        ]
        assert v.validate_json_structure(
            {"a": {"b": 1.5}}, required=["a.b"], types={"a.b": (int, float)}
        )
        assert "Invalid JSON" in v.validate_json_structure("{nope").message
        assert "object" in v.validate_json_structure("[1, 2]").message
