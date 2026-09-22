"""Composition layer: frames, banners, menus and input prompts.

Contains no personal content -- every string it renders is handed to it by
``messages.py``.
"""

from __future__ import annotations

from . import animation as anim
from .animation import C, paint


# ---------------------------------------------------------------------------
# Border sets (Unicode, with an ASCII fallback for stubborn code pages)
# ---------------------------------------------------------------------------

class _Chars:
    if anim.UNICODE:
        H = "═"; V = "║"; TL = "╔"; TR = "╗"; BL = "╚"; BR = "╝"
        h = "─"; v = "│"; tl = "╭"; tr = "╮"; bl = "╰"; br = "╯"
        ml = "├"; mr = "┤"
        DOT = "·"
        RULE = "─"
    else:  # pragma: no cover - only on legacy code pages
        H = "="; V = "|"; TL = "+"; TR = "+"; BL = "+"; BR = "+"
        h = "-"; v = "|"; tl = "+"; tr = "+"; bl = "+"; br = "+"
        ml = "+"; mr = "+"
        DOT = "."
        RULE = "-"


G = _Chars()


def _pad_to(width: int) -> int:
    return max(30, width)


def _line(text: str, inner: int) -> str:
    """Centre `text` inside a box of `inner` printable columns."""
    text = text[:inner]
    left = (inner - len(text)) // 2
    right = inner - len(text) - left
    return " " * left + text + " " * right


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def double_box(lines, width: int | None = None, color: str = "", text_color: str = "",
               animate: bool = True) -> None:
    """The heavy ╔══╗ frame, used for the banner and big moments."""
    width = _pad_to(width or anim.width(60))
    inner = width - 2
    color = color or C.DEEP_ROSE
    text_color = text_color or C.IVORY
    pad = max(0, (anim.term_columns() - width) // 2)
    prefix = " " * pad

    rows = [G.TL + G.H * inner + G.TR]
    for text in lines:
        rows.append(G.V + _line(text, inner) + G.V)
    rows.append(G.BL + G.H * inner + G.BR)

    for i, row in enumerate(rows):
        if i == 0 or i == len(rows) - 1 or not row[1:-1].strip():
            anim.write(prefix + paint(row, color) + "\n")
        else:
            body = row[1:-1]
            anim.write(
                prefix
                + paint(G.V, color)
                + paint(body, C.BOLD + text_color if anim.COLOR else "")
                + paint(G.V, color)
                + "\n"
            )
        anim.flush()
        if animate:
            anim.sleep(0.05)


def light_box(lines, width: int | None = None, color: str = "", title: str | None = None,
              animate: bool = True) -> None:
    """The light ╭──╮ frame, used for menus and quieter panels."""
    width = _pad_to(width or anim.width(52))
    inner = width - 2
    color = color or C.PLUM
    pad = max(0, (anim.term_columns() - width) // 2)
    prefix = " " * pad

    anim.write(prefix + paint(G.tl + G.h * inner + G.tr, color) + "\n")
    if title is not None:
        anim.write(
            prefix
            + paint(G.v, color)
            + paint(_line(title, inner), C.BOLD + C.IVORY if anim.COLOR else "")
            + paint(G.v, color)
            + "\n"
        )
        anim.write(prefix + paint(G.ml + G.h * inner + G.mr, color) + "\n")

    for text in lines:
        anim.write(
            prefix
            + paint(G.v, color)
            + paint(_line(text, inner), C.SOFT)
            + paint(G.v, color)
            + "\n"
        )
        anim.flush()
        if animate:
            anim.sleep(0.03)
    anim.write(prefix + paint(G.bl + G.h * inner + G.br, color) + "\n")
    anim.flush()


def rule(width: int | None = None, color: str = "") -> None:
    width = width or anim.width(46)
    pad = max(0, (anim.term_columns() - width) // 2)
    anim.write(" " * pad + paint(G.RULE * width, color or C.FAINT) + "\n")
    anim.flush()


def blank(count: int = 1) -> None:
    anim.write("\n" * count)
    anim.flush()


def spaced_name(name: str) -> str:
    return " ".join(name.upper())


# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------

def banner(name: str, tagline: str = "", animate: bool = True) -> None:
    """The main ╔══╗ title card."""
    lines = ["", spaced_name(name), ""]
    if tagline:
        lines += [tagline, ""]
    double_box(lines, width=anim.width(60), animate=animate)


def section_header(title: str, color: str = "") -> None:
    """A small centred heading with a rule under it."""
    blank()
    anim.write(anim.center(paint(title.upper(), C.BOLD + (color or C.ROSE) if anim.COLOR else "")) + "\n")
    rule(width=max(len(title) + 8, 24))
    blank()


def quiet(text: str, color: str = "") -> None:
    """A single dim centred line, printed instantly."""
    anim.write(anim.center(paint(text, color or C.DIM)) + "\n")
    anim.flush()


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def menu(title: str, items, width: int | None = None) -> None:
    """Render the option list inside a light frame, left-aligned inside."""
    width = _pad_to(width or anim.width(52))
    inner = width - 2
    pad = max(0, (anim.term_columns() - width) // 2)
    prefix = " " * pad
    color = C.PLUM

    anim.write(prefix + paint(G.tl + G.h * inner + G.tr, color) + "\n")
    anim.write(
        prefix
        + paint(G.v, color)
        + paint(_line(title, inner), C.BOLD + C.IVORY if anim.COLOR else "")
        + paint(G.v, color)
        + "\n"
    )
    anim.write(prefix + paint(G.ml + G.h * inner + G.mr, color) + "\n")
    anim.write(prefix + paint(G.v, color) + " " * inner + paint(G.v, color) + "\n")

    # Left margin that keeps the list visually centred as a block.
    longest = max(len(label) for _, label, _ in items) + 6
    margin = max(2, (inner - longest) // 2)

    for key, label, _handler in items:
        body = "%s[%s] %s" % (" " * margin, key, label)
        body = body + " " * max(0, inner - len(body))
        anim.write(prefix + paint(G.v, color))
        anim.write(paint(" " * margin, ""))
        anim.write(paint("[%s]" % key, C.ROSE))
        anim.write(paint(" " + label, C.IVORY))
        used = margin + len(key) + 3 + len(label)
        anim.write(" " * max(0, inner - used))
        anim.write(paint(G.v, color) + "\n")
        anim.flush()
        anim.sleep(0.035)

    anim.write(prefix + paint(G.v, color) + " " * inner + paint(G.v, color) + "\n")
    anim.write(prefix + paint(G.bl + G.h * inner + G.br, color) + "\n")
    anim.flush()


def choice_list(options, start: int = 1) -> None:
    """A simple centred [1] Label list, no frame."""
    longest = max(len(opt) for opt in options) + 5
    pad = max(0, (anim.term_columns() - longest) // 2)
    for i, option in enumerate(options, start=start):
        anim.write(" " * pad + paint("[%d]" % i, C.ROSE) + " " + paint(option, C.IVORY) + "\n")
        anim.flush()
        anim.sleep(0.05)


def key_list(pairs) -> None:
    """A centred [Y] Label list for letter choices."""
    longest = max(len(label) for _, label in pairs) + 5
    pad = max(0, (anim.term_columns() - longest) // 2)
    for key, label in pairs:
        anim.write(" " * pad + paint("[%s]" % key, C.ROSE) + " " + paint(label, C.IVORY) + "\n")
        anim.flush()
        anim.sleep(0.05)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

class Quit(Exception):
    """Raised when the reader hits EOF -- treated as a graceful goodbye."""


def _clean(text: str) -> str:
    """Strip whitespace, stray carriage returns and any byte-order mark.

    PowerShell prefixes piped input with a BOM, which would otherwise make
    a perfectly good "9" look like an invalid choice.
    """
    return text.replace("﻿", "").replace("\r", "").strip()


def ask(prompt: str = "", color: str = "") -> str:
    """Read one line. Raises Quit on EOF so Ctrl+D behaves like Exit."""
    marker = paint("  " + (prompt or ">") + " ", color or C.ROSE)
    pad = max(0, (anim.term_columns() - 40) // 2)
    try:
        anim.show_cursor()
        return _clean(input(" " * pad + marker))
    except EOFError:
        raise Quit()


def ask_raw(prompt: str = ">", indent: int = 0) -> str:
    """Read one line without stripping interior spacing (message composer)."""
    try:
        anim.show_cursor()
        line = input(" " * indent + paint(prompt + " ", C.ROSE))
    except EOFError:
        raise Quit()
    return line.replace("﻿", "").replace("\r", "")


def pause(text: str = "Press Enter to continue") -> None:
    """A dim centred prompt that waits for Enter."""
    blank()
    line = "[ %s ]" % text
    pad = max(0, (anim.term_columns() - len(line)) // 2)
    try:
        anim.show_cursor()
        input(" " * pad + paint(line, C.FAINT))
    except EOFError:
        raise Quit()
    anim.hide_cursor()


def confirm_keys(valid, prompt: str = ">") -> str:
    """Loop until the reader presses one of `valid` (case-insensitive)."""
    valid = [v.lower() for v in valid]
    while True:
        answer = ask(prompt).lower()
        if answer in valid:
            return answer
        quiet("Not one of the options.", C.WINE)
