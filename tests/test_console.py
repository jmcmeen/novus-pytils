"""Tests for novus_pytils.console."""

import io
from unittest.mock import patch

import pytest

from novus_pytils import console
from novus_pytils.console import Color


@pytest.fixture(autouse=True)
def _auto_color() -> None:
    console.use_color(None)
    yield
    console.use_color(None)


class TestColor:
    def test_codes_and_backgrounds(self) -> None:
        assert Color.RED.value == "\033[31m" and Color.RESET.value == "\033[0m"
        assert Color.WHITE.background == "\033[47m"
        assert Color.BOLD.background == ""

    def test_supports_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        tty = io.StringIO()
        tty.isatty = lambda: True  # type: ignore[method-assign]
        for var in ("NO_COLOR", "FORCE_COLOR"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("TERM", "xterm-256color")
        assert console.supports_color(tty)
        assert not console.supports_color(io.StringIO())
        monkeypatch.setenv("NO_COLOR", "1")
        assert not console.supports_color(tty)
        monkeypatch.delenv("NO_COLOR")
        monkeypatch.setenv("TERM", "dumb")
        assert not console.supports_color(tty)
        monkeypatch.setenv("FORCE_COLOR", "1")
        assert console.supports_color(io.StringIO())

    def test_print_color_respects_override_and_argument(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        console.use_color(True)
        console.print_color("hi", Color.RED, background=Color.WHITE)
        assert capsys.readouterr().out == "\033[31m\033[47mhi\033[0m\n"
        console.use_color(False)
        console.print_color("hi", Color.RED)
        assert capsys.readouterr().out == "hi\n"
        console.print_color("hi", Color.RED, color_enabled=True, end="")
        assert capsys.readouterr().out == "\033[31mhi\033[0m"

    def test_status_lines(self, capsys: pytest.CaptureFixture) -> None:
        console.use_color(False)
        console.print_success("ok")
        console.print_warning("hmm")
        console.print_info("fyi")
        console.print_error("bad")
        out, err = capsys.readouterr()
        assert out == "✓ ok\n⚠ hmm\nℹ fyi\n" and err == "✗ bad\n"


class TestTable:
    def test_format_table(self) -> None:
        text = console.format_table(
            ["Name", "Age"], [["Al", 3], ["Beatrice", 42]], align=["left", "right"]
        )
        assert text.splitlines() == [
            "Name     | Age",
            "--------------",
            "Al       |   3",
            "Beatrice |  42",
        ]
        assert console.format_table(["a"], [], separator="|").splitlines() == ["a", "-"]
        assert console.format_table(["ab"], [["x"]], align=["center"]).splitlines()[2] == "x "

    def test_print_table(self, capsys: pytest.CaptureFixture) -> None:
        console.print_table(["h"], [[1]])
        assert capsys.readouterr().out == "h\n-\n1\n"
        console.print_table([], [])
        assert capsys.readouterr().out == ""


class TestProgressBar:
    def test_draws_and_finishes(self) -> None:
        out = io.StringIO()
        console.print_progress_bar(0, 4, width=4, stream=out)
        console.print_progress_bar(2, 4, prefix="p ", suffix="s", width=4, stream=out)
        console.print_progress_bar(4, 4, width=4, stream=out)
        text = out.getvalue()
        assert text.startswith("\r|----|   0.0% ")
        assert "\rp |██--|  50.0% s" in text
        assert text.endswith("\r|████| 100.0% \n")
        out = io.StringIO()
        console.print_progress_bar(3, 0, width=2, stream=out)
        assert out.getvalue() == "\r|--|   0.0% "


class TestPrompts:
    def test_confirm(self) -> None:
        with patch("builtins.input", side_effect=["y"]) as inp:
            assert console.confirm("Go?") is True
            inp.assert_called_once_with("Go? [y/N]: ")
        with patch("builtins.input", side_effect=["", "maybe", "NO"]):
            assert console.confirm("Go?", default=True) is True
            assert console.confirm("Go?") is False

    def test_prompt(self, capsys: pytest.CaptureFixture) -> None:
        console.use_color(False)
        with patch("builtins.input", side_effect=["  v  "]) as inp:
            assert console.prompt("Name") == "v"
            inp.assert_called_once_with("Name: ")
        with patch("builtins.input", side_effect=[""]) as inp:
            assert console.prompt("Name", default="d") == "d"
            inp.assert_called_once_with("Name [d]: ")
        with patch("builtins.input", side_effect=["", "x"]):
            assert console.prompt("Name", required=True) == "x"
        with patch("builtins.input", side_effect=["bad", "good"]):
            assert console.prompt("Name", validator=lambda s: s == "good") == "good"
        with patch("builtins.input", side_effect=[""]):
            assert console.prompt("Name") == ""
        assert "required" in capsys.readouterr().err


def test_clear_and_move() -> None:
    out = io.StringIO()
    console.clear_screen(out)
    console.move_cursor(5, 10, out)
    assert out.getvalue() == "\033[2J\033[H\033[5;10H"
