#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_pad_tool.py

"""Display-width-aware text padding / truncation tool (pure stdlib).

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text layout helper
agents can call when preparing output for terminals, chat bubbles or
fixed-width reports.  It complements the wrapping and table-rendering
tools: instead of reflowing paragraphs or drawing borders, it pads,
zero-fills, hard-truncates and measures single chunks of text in
*display columns* rather than characters.

The tool supports four modes:

* ``pad`` — pad the text to a total display width using ``align``
  (``left`` / ``right`` / ``center``, the width-aware counterparts of
  ``str.ljust`` / ``str.rjust`` / ``str.center``) and a single fill
  character (``fill_char``, default one space).  When the padding of a
  ``center`` call cannot split evenly the extra column goes to the
  **right** side (``left = floor(remaining / 2)``).
* ``zfill`` — zero-pad to the width while preserving a leading ``+`` /
  ``-`` sign (the width-aware counterpart of ``str.zfill``); the zeros
  are inserted *after* the sign.
* ``truncate_to_width`` — hard-cut the text at the display width,
  optionally appending a ``marker`` (default ``"…"``) *within* the
  width: the content is cut to ``width - marker_width`` columns first,
  so the result never exceeds the requested width.
* ``width`` — report the display width of the text in columns (plus
  its character count), the measurement primitive all other modes
  use.

East-asian width awareness
--------------------------

``str.ljust`` and friends count *characters*, not display columns:
``"中文"`` is two characters but occupies four terminal columns, so
latin padding rules misalign any mixed CJK / latin column.  This tool
measures every character the same way the wrapping tool does:

* every character whose ``unicodedata.east_asian_width`` is ``W`` or
  ``F`` counts as **2** columns — CJK ideographs, kana, hangul,
  fullwidth forms and (per Unicode's own width tables) nearly all
  emoji, including astral-plane ones such as ``"🌍"``;
* combining marks and format characters (``unicodedata.category``
  ``Mn`` / ``Me`` / ``Cf``, or a non-zero ``unicodedata.combining``
  class) count as **0** columns and stay glued to the character they
  follow when truncating;
* everything else — latin letters, digits, halfwidth katakana, and
  *ambiguous* characters such as ``"…"`` — counts as 1 column.

Rules worth pinning
-------------------

* ``pad`` / ``zfill`` with a text already at least as wide as ``width``
  return the text **unchanged** (mirroring ``str.ljust`` /
  ``str.zfill``) instead of raising.
* ``truncate_to_width`` with a text at most as wide as ``width``
  returns it unchanged (``truncated: False``).
* A hard cut can split between two columns of one wide character: the
  character is never split in half, so a plain cut of ``"中中"`` to
  width 3 yields ``"中"`` (2 columns, one column short) — the result
  never *exceeds* the requested width.
* ``fill_char`` must be exactly one character occupying exactly one
  column (combining / format characters and wide characters are
  rejected — they cannot fill a 1-column unit unambiguously).
* ``marker`` must be visible (display width >= 1), at most 10
  characters and 10 columns wide, and no wider than ``width`` itself;
  it defaults to ``"…"`` and an empty string (``marker=""``) selects a
  plain hard cut without one.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode / align,
missing or non-integer or out-of-range width, illegal fill character
or marker, oversized text) raise a ``ValueError``, mirroring the other
common tools.  The padding pipeline itself cannot fail on content —
every representable input produces a deterministic result.
"""

import unicodedata
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Default truncation marker (U+2026 HORIZONTAL ELLIPSIS — an
# *ambiguous*-width character, i.e. one column under this tool's rules).
DEFAULT_MARKER = "…"


def _char_width(char: str) -> int:
    """Return the display width in columns of a single character."""
    if unicodedata.combining(char):
        return 0
    if unicodedata.category(char) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1


def _display_width(text: str) -> int:
    """Return the total display width in columns of a string."""
    return sum(_char_width(char) for char in text)


def _slice_by_width(text: str, budget: int) -> Tuple[str, int]:
    """Return the longest prefix of ``text`` whose width is <= budget.

    Zero-width characters (combining marks, format characters) always
    fit within any non-negative budget, so a cut keeps the marks glued
    to the visible character they follow.  A wide character that would
    straddle the budget stops the slice early (it is never split).
    """
    taken: List[str] = []
    width_sum = 0
    for char in text:
        char_w = _char_width(char)
        if width_sum + char_w > budget:
            break
        taken.append(char)
        width_sum += char_w
    return "".join(taken), width_sum


class TextPadTool(Tool):
    """Display-width-aware padding / zfill / truncation / width tool.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_pad_tool"
    description: str = (
        "Text pad tool — pure Python stdlib, no network required, with "
        "east-asian (CJK) display-width awareness. Pad text to a total "
        "display width with left/right/center alignment and a "
        "single-character fill (mode='pad'), zero-pad to the width while "
        "preserving a leading + / - sign (mode='zfill'), hard-cut text at "
        "a display width with an optional '…' marker kept within the "
        "width (mode='truncate_to_width'), or report the display width of "
        "a text in columns (mode='width'). Wide CJK/fullwidth characters "
        "count as two columns and combining marks as zero, so padded CJK "
        "and latin text aligns in terminal columns."
    )

    MODES: ClassVar[tuple] = ("pad", "zfill", "truncate_to_width", "width")
    ALIGNS: ClassVar[tuple] = ("left", "right", "center")

    MIN_WIDTH: ClassVar[int] = 0
    MAX_WIDTH: ClassVar[int] = 10_000

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        width: Any = None,
        align: Any = None,
        fill_char: Any = None,
        marker: Any = None,
    ) -> Dict[str, Any]:
        """Run one padding / truncation / measurement operation.

        Args:
            mode (str): One of ``pad`` / ``zfill`` /
                ``truncate_to_width`` / ``width``.
            text (str): The text to process (non-empty string, at most
                100,000 characters).
            width (int): Total display width in columns — 0 to 10,000;
                required for the ``pad``, ``zfill`` and
                ``truncate_to_width`` modes; not used by ``width`` mode.
            align (str): ``pad`` mode only — ``left`` (default),
                ``right`` or ``center``.
            fill_char (str): ``pad`` mode only — exactly one character
                occupying one display column (default ``" "``);
                combining and wide characters are rejected.
            marker (str): ``truncate_to_width`` mode only — string
                appended within the width when content is dropped
                (default ``"…"``); an empty string disables it.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string — an integer for ``width`` mode — plus the call
                context, including ``input_width`` and, for
                ``truncate_to_width``, ``truncated`` /
                ``dropped_chars``).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        if mode == "width":
            measured = _display_width(clean_text)
            return {
                "mode": "width",
                "width": measured,
                "character_count": len(clean_text),
                "result": measured,
            }
        clean_width = self._validate_width(width)
        if mode == "pad":
            return self._run_pad(clean_text, clean_width, align, fill_char)
        if mode == "zfill":
            return self._run_zfill(clean_text, clean_width)
        return self._run_truncate(clean_text, clean_width, marker)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_pad_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any) -> str:
        """Validate the ``text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"text must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid("text must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(
                f"text exceeds the {100_000:,}-character limit "
                f"(got {len(text):,} characters)"
            )
        return text

    @classmethod
    def _validate_width(cls, width: Any) -> int:
        """Validate the required ``width`` option."""
        if width is None:
            cls._invalid(
                "width is required for the pad, zfill and "
                "truncate_to_width modes (got None)"
            )
        if isinstance(width, bool) or not isinstance(width, int):
            cls._invalid(
                f"width must be an integer between {cls.MIN_WIDTH} and "
                f"{cls.MAX_WIDTH:,} (got {width!r})"
            )
        if not cls.MIN_WIDTH <= width <= cls.MAX_WIDTH:
            cls._invalid(
                f"width must be between {cls.MIN_WIDTH} and "
                f"{cls.MAX_WIDTH:,} inclusive (got {width})"
            )
        return width

    @classmethod
    def _validate_align(cls, align: Any) -> str:
        """Validate the pad-mode ``align`` selector."""
        if align is None:
            return "left"
        if align not in cls.ALIGNS:
            cls._invalid(
                f"align must be one of: {', '.join(cls.ALIGNS)} "
                f"(got {align!r})"
            )
        return align

    @classmethod
    def _validate_fill_char(cls, fill_char: Any) -> str:
        """Validate the pad-mode ``fill_char``.

        Accepts ``None`` (one space).  Any other value must be exactly
        one character whose display width is exactly one column:
        combining / format characters (0 columns) and wide characters
        (2 columns) cannot fill a one-column unit unambiguously.
        """
        if fill_char is None:
            return " "
        if (
            isinstance(fill_char, bool)
            or not isinstance(fill_char, str)
            or len(fill_char) != 1
        ):
            cls._invalid(
                f"fill_char must be a single character (got {fill_char!r})"
            )
        char_w = _char_width(fill_char)
        if char_w == 0:
            cls._invalid(
                "fill_char must occupy one display column; combining and "
                f"format characters occupy zero (got {fill_char!r})"
            )
        if char_w == 2:
            cls._invalid(
                "fill_char must occupy one display column; wide "
                f"east-asian characters occupy two (got {fill_char!r})"
            )
        return fill_char

    @classmethod
    def _validate_marker(cls, marker: Any, width: int) -> Optional[str]:
        """Validate the truncate-mode ``marker`` against ``width``.

        ``None`` selects the default ``"…"`` and ``""`` explicitly
        disables the marker (plain hard cut).  Any other value must be
        a string of at most 10 characters whose display width is 1 to
        10 columns, and no wider than ``width`` itself so the marker
        always fits within the requested width.
        """
        if marker is None:
            return DEFAULT_MARKER
        if marker == "":
            return None
        if isinstance(marker, bool) or not isinstance(marker, str):
            cls._invalid(
                f"marker must be a string, None or '' (got {marker!r})"
            )
        if len(marker) > 10:
            cls._invalid(
                f"marker exceeds the 10-character limit "
                f"(got {len(marker)} characters)"
            )
        marker_w = _display_width(marker)
        if marker_w < 1:
            cls._invalid(
                "marker must contain at least one visible character; "
                "zero-width strings cannot mark a truncation "
                f"(got {marker!r})"
            )
        if marker_w > 10:
            cls._invalid(
                "marker must be at most 10 display columns wide "
                f"(got {marker_w})"
            )
        if marker_w > width:
            cls._invalid(
                f"marker display width ({marker_w}) must not exceed width "
                f"({width}); pass marker='' for a plain hard cut"
            )
        return marker

    # ------------------------------------------------------------------ #
    # pad mode
    # ------------------------------------------------------------------ #

    def _run_pad(
        self, text: str, width: int, align: Any, fill_char: Any
    ) -> Dict[str, Any]:
        """Pad the text to ``width`` columns (ljust/rjust/center)."""
        clean_align = self._validate_align(align)
        clean_fill = self._validate_fill_char(fill_char)
        input_width = _display_width(text)
        context: Dict[str, Any] = {
            "mode": "pad",
            "width": width,
            "align": clean_align,
            "fill_char": clean_fill,
            "input_width": input_width,
        }
        remaining = width - input_width
        if remaining <= 0:
            # Already at least as wide as the target: unchanged,
            # mirroring str.ljust / str.rjust / str.center.
            return {**context, "result": text}
        if clean_align == "left":
            result = text + clean_fill * remaining
        elif clean_align == "right":
            result = clean_fill * remaining + text
        else:
            # Odd remainders put the extra column on the right.
            left = remaining // 2
            result = (
                clean_fill * left + text + clean_fill * (remaining - left)
            )
        return {**context, "result": result}

    # ------------------------------------------------------------------ #
    # zfill mode
    # ------------------------------------------------------------------ #

    def _run_zfill(self, text: str, width: int) -> Dict[str, Any]:
        """Zero-pad to ``width`` while preserving a leading + / - sign."""
        input_width = _display_width(text)
        context: Dict[str, Any] = {
            "mode": "zfill",
            "width": width,
            "input_width": input_width,
            "sign": None,
        }
        if input_width >= width:
            # Mirroring str.zfill: never shortens, never errors.
            if text[0] in "+-":
                context["sign"] = text[0]
            return {**context, "result": text}
        sign = text[0] if text[0] in "+-" else ""
        result = sign + "0" * (width - input_width) + text[len(sign):]
        context["sign"] = sign or None
        return {**context, "result": result}

    # ------------------------------------------------------------------ #
    # truncate_to_width mode
    # ------------------------------------------------------------------ #

    def _run_truncate(
        self, text: str, width: int, marker: Any
    ) -> Dict[str, Any]:
        """Hard-cut the text at ``width`` columns, marker kept within."""
        clean_marker = self._validate_marker(marker, width)
        input_width = _display_width(text)
        context: Dict[str, Any] = {
            "mode": "truncate_to_width",
            "width": width,
            "marker": clean_marker,
            "input_width": input_width,
        }
        if input_width <= width:
            return {
                **context,
                "truncated": False,
                "dropped_chars": 0,
                "result": text,
            }
        budget = width - _display_width(clean_marker) if clean_marker else width
        content, _ = _slice_by_width(text, budget)
        result = content + clean_marker if clean_marker else content
        return {
            **context,
            "truncated": True,
            "dropped_chars": len(text) - len(content),
            "result": result,
        }
