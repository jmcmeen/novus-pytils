"""Terminal output without a dependency: colours, status lines, tables, a progress bar, prompts.

Colour is used only when stdout is a terminal, ``NO_COLOR`` is unset, and
``TERM`` is not ``dumb``. Pass ``color=False`` to any printer to force plain
text, or call :func:`use_color` to decide globally.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Iterable, Sequence
from enum import Enum
from typing import Any


class Color(str, Enum):
    """ANSI SGR codes. Background colours are the foreground code plus 10."""

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    @property
    def background(self) -> str:
        """This colour as a background code (foreground colours only)."""
        code = int(self.value[2:-1])
        return f"\033[{code + 10}m" if 30 <= code <= 37 else ""


def supports_color(stream: Any = None) -> bool:
    """Whether ``stream`` (default stdout) is a terminal that should get colour."""
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


_color_override: bool | None = None


def use_color(enabled: bool | None) -> None:
    """Force colour on or off for every printer here; ``None`` goes back to auto-detect."""
    global _color_override
    _color_override = enabled


def _colored(text: str, color: Color, background: Color | None, enabled: bool | None) -> str:
    on = (
        enabled
        if enabled is not None
        else (_color_override if _color_override is not None else supports_color())
    )
    if not on:
        return text
    return f"{color.value}{background.background if background else ''}{text}{Color.RESET.value}"


def print_color(
    text: str,
    color: Color,
    background: Color | None = None,
    color_enabled: bool | None = None,
    **kwargs: Any,
) -> None:
    """Print ``text`` in a colour (when the terminal supports it). ``kwargs`` go to :func:`print`."""
    print(_colored(text, color, background, color_enabled), **kwargs)


def print_success(text: str, **kwargs: Any) -> None:
    """Green tick line."""
    print_color(f"✓ {text}", Color.GREEN, **kwargs)


def print_error(text: str, **kwargs: Any) -> None:
    """Red cross line, to stderr by default."""
    kwargs.setdefault("file", sys.stderr)
    print_color(f"✗ {text}", Color.RED, **kwargs)


def print_warning(text: str, **kwargs: Any) -> None:
    """Yellow warning line."""
    print_color(f"⚠ {text}", Color.YELLOW, **kwargs)


def print_info(text: str, **kwargs: Any) -> None:
    """Blue info line."""
    print_color(f"ℹ {text}", Color.BLUE, **kwargs)


def format_table(
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    align: Sequence[str] | None = None,
    separator: str = " | ",
) -> str:
    """Lay out rows under headers with a rule beneath the headers.

    Args:
        headers: Column titles.
        rows: Cell values; ``str()`` is applied.
        align: Per column, ``"left"`` (default), ``"right"`` or ``"center"``.
        separator: Between columns.
    """
    table = [[str(c) for c in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in table:
        for i, cell in enumerate(row[: len(widths)]):
            widths[i] = max(widths[i], len(cell))
    align = list(align or [])

    def fmt(cells: Sequence[str]) -> str:
        out = []
        for i, w in enumerate(widths):
            cell = cells[i] if i < len(cells) else ""
            how = align[i] if i < len(align) else "left"
            out.append(
                cell.rjust(w)
                if how == "right"
                else cell.center(w)
                if how == "center"
                else cell.ljust(w)
            )
        return separator.join(out)

    lines = [fmt(list(headers)), "-" * len(fmt(list(headers)))]
    lines.extend(fmt(row) for row in table)
    return "\n".join(lines)


def print_table(headers: Sequence[str], rows: Iterable[Sequence[Any]], **kwargs: Any) -> None:
    """Print :func:`format_table`'s output. Nothing is printed for empty headers."""
    if headers:
        print(format_table(headers, rows, **kwargs))


def print_progress_bar(
    done: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    width: int = 40,
    fill: str = "█",
    stream: Any = None,
) -> None:
    """Redraw a single-line progress bar; prints a newline once ``done >= total``.

    A ``total`` of 0 draws an empty bar at 0%.
    """
    stream = stream or sys.stdout
    fraction = min(done / total, 1.0) if total > 0 else 0.0
    filled = int(width * fraction)
    bar = fill * filled + "-" * (width - filled)
    stream.write(f"\r{prefix}|{bar}| {fraction * 100:5.1f}% {suffix}")
    if total > 0 and done >= total:
        stream.write("\n")
    stream.flush()


def confirm(message: str, default: bool = False) -> bool:
    """Ask a yes/no question; Enter picks ``default``. Re-asks on anything unrecognised."""
    hint = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{message} [{hint}]: ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False


def prompt(
    message: str,
    default: str | None = None,
    required: bool = False,
    validator: Callable[[str], bool] | None = None,
) -> str:
    """Ask for a line of text.

    Args:
        message: The question; ``[default]`` is appended when one is given.
        default: Returned on an empty answer.
        required: Re-ask on an empty answer with no default.
        validator: Re-ask while this returns False.
    """
    text = f"{message} [{default}]: " if default is not None else f"{message}: "
    while True:
        answer = input(text).strip()
        if not answer:
            if default is not None:
                return default
            if required:
                print_error("A value is required.")
                continue
            return ""
        if validator is not None and not validator(answer):
            print_error("That value is not valid.")
            continue
        return answer


def clear_screen(stream: Any = None) -> None:
    """Clear the terminal with ANSI codes (no subprocess)."""
    stream = stream or sys.stdout
    stream.write("\033[2J\033[H")
    stream.flush()


def move_cursor(row: int, column: int, stream: Any = None) -> None:
    """Move the cursor to a 1-based row and column."""
    stream = stream or sys.stdout
    stream.write(f"\033[{row};{column}H")
    stream.flush()
