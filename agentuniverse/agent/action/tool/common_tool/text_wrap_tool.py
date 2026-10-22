#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: text_wrap_tool.py

"""Text wrapping / reflow utility tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency text layout helper
agents can call when preparing output for terminals, chat bubbles or
fixed-width reports: wrapping paragraphs, reflowing them into single
strings, normalizing indentation, prefixing lines, and truncating long
text to a display budget.

The tool supports five modes:

* ``wrap`` — wrap text to a display width and return the list of
  wrapped lines.  Explicit newlines in the input are honored as hard
  paragraph breaks (``"a\\n\\nb"`` keeps its blank line), unlike the
  stdlib, which converts newlines to spaces.  Whitespace-only input
  lines are emitted as empty output lines.
* ``fill`` — wrap the same way and join the lines into a single string
  with a configurable separator (default ``"\\n"``, matching
  ``textwrap.fill`` for pure-latin single-paragraph input).
* ``dedent`` — remove the longest common leading whitespace from every
  line (delegates to ``textwrap.dedent``).
* ``indent`` — add a prefix to the beginning of every non-blank line
  (lines containing at least one non-whitespace character; delegates
  to ``textwrap.indent``).
* ``shorten`` — collapse whitespace and truncate the text to the
  display width, appending the placeholder ``"…"`` when anything is
  dropped (the width-aware counterpart of ``textwrap.shorten``).

East-asian width awareness
--------------------------

``textwrap`` counts *characters*, not display columns: ten CJK
ideographs occupy twenty terminal columns but are measured as ten.
This tool therefore runs its own greedy wrapper loop — mirroring the
``textwrap.TextWrapper`` chunk algorithm (whitespace chunks kept
mid-line and dropped at line edges, hyphen splitting through the very
same word-separation pattern, long-word breaking) — over *display
width* units instead:

* every character whose ``unicodedata.east_asian_width`` is ``W`` or
  ``F`` counts as **2** columns, everything else as 1;
* combining marks and format characters
  (``unicodedata.category`` ``Mn`` / ``Me`` / ``Cf``, or a non-zero
  ``unicodedata.combining`` class) count as 0 columns and stay glued
  to the unit they follow, so grapheme-ish clusters never split;
* wide characters are individually breakable (standard simplified CJK
  wrapping — a break is allowed between any two wide units; full
  kinsoku shori line-start/line-end punctuation rules are not
  applied);
* hyphenation (``break_on_hyphens``) is a latin-run heuristic and is
  only applied to chunks without wide characters, so pure-latin input
  wraps byte-for-byte identically to ``textwrap`` while mixed CJK and
  latin text aligns to the requested width in terminal columns.

Options: ``width`` (1-200, default 80), ``break_long_words`` and
``break_on_hyphens`` (both default ``True``, matching ``textwrap``),
``max_lines`` (truncate wrapped output to at most this many lines,
appending an overflow marker ``"… [+N chars]"`` where *N* is the
number of dropped content characters — not counting whitespace
separators and line indents), and ``initial_indent`` /
``subsequent_indent`` for the ``wrap`` and ``fill`` modes.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode, width
outside 1-200, ``max_lines`` below 1, non-boolean break flags, indents
containing hard newlines or wider than (or as wide as) ``width``,
empty / oversized ``prefix`` / ``separator``) raise a ``ValueError``,
mirroring the other common tools.  The wrap pipeline itself cannot
fail on content — every representable input either wraps or (only when
a single wide character cannot fit the remaining line budget while
breaking long words) produces one overlong line rather than looping.
"""

import re
import textwrap
import unicodedata
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Word-separation pattern copied verbatim from the stdlib
# (textwrap.TextWrapper.wordsep_re, CPython 3.11) so that latin runs —
# hyphenated words such as "goof-ball", em-dash pairs such as "--" —
# split into exactly the same indivisible chunks textwrap produces.
_WORD_PUNCT = r"[\w!\"\'&.,?]"
_LETTER = r"[^\d\W]"
_NOWHITESPACE = "[^ \t\n\r\f\v]"
_WORDSEP_RE = re.compile(
    r"""
    ( # any whitespace
      [ \t\n\r\f\v]+
    | # em-dash between words
      (?<=%(wp)s) -{2,} (?=\w)
    | # word, possibly hyphenated
      %(nws)s+? (?:
          # hyphenated word
            -(?: (?<=%(lt)s{2}-) | (?<=%(lt)s-%(lt)s-))
                (?= %(lt)s -? %(lt)s)
        | # end of word
          (?=[ \t\n\r\f\v]|\Z)
        | # em-dash
          (?<=%(wp)s) (?=-{2,}\w)
      )
    )"""
    % {"wp": _WORD_PUNCT, "lt": _LETTER, "nws": _NOWHITESPACE},
    re.VERBOSE,
)
del _WORD_PUNCT, _LETTER, _NOWHITESPACE

# Whitespace-run splitter used when break_on_hyphens is disabled
# (mirrors textwrap.TextWrapper.wordsep_simple_re).
_WHITESPACE_RUN_RE = re.compile(r"( +)")

# Overflow / truncation markers.
_OVERFLOW_PREFIX = "… [+"
_OVERFLOW_SUFFIX = " chars]"
_SHORTEN_PLACEHOLDER = "…"

# A wrapped unit: (text, display_width, is_whitespace).
_Unit = Tuple[str, int, bool]


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


def _is_wide(char: str) -> bool:
    """Return True for east-asian wide / fullwidth characters."""
    return unicodedata.east_asian_width(char) in ("W", "F")


def _slice_by_width(text: str, budget: int) -> Tuple[str, int]:
    """Return the longest prefix of ``text`` whose width is <= budget."""
    taken: List[str] = []
    width_sum = 0
    for char in text:
        char_w = _char_width(char)
        if width_sum + char_w > budget:
            break
        taken.append(char)
        width_sum += char_w
    return "".join(taken), width_sum


def _build_units(text: str, break_on_hyphens: bool) -> List[_Unit]:
    """Split one hard line into width-carrying, breakable units.

    First the line is split with the stdlib word-separation semantics
    (identical to ``textwrap.TextWrapper._split``), then any chunk
    that contains wide characters is further split so that each wide
    grapheme-ish unit stands alone and becomes an individual break
    opportunity.  Pure-latin chunks survive untouched, which is what
    makes pure-latin output byte-identical to ``textwrap``.  Zero-width
    characters (combining marks, format characters) always stay glued
    to the unit they follow.
    """
    raw_chunks = _WORDSEP_RE.split(text) if break_on_hyphens else _WHITESPACE_RUN_RE.split(text)
    units: List[_Unit] = []
    for chunk in raw_chunks:
        if not chunk:
            continue
        if not chunk.strip():
            # Whitespace run: kept as one chunk, one column per space.
            units.append((chunk, len(chunk), True))
            continue
        # groups: [text, width, kind] with kind 'n' (narrow run) or 'w'.
        groups: List[List[Any]] = []
        lead_zero = ""
        zwj_pending = False
        for char in chunk:
            width = _char_width(char)
            if width == 0:
                if groups:
                    groups[-1][0] += char
                else:
                    lead_zero += char
                zwj_pending = char == "\u200d" and bool(groups)
            elif _is_wide(char):
                if zwj_pending:
                    # A wide character right after a zero-width joiner
                    # extends the joined group (e.g. emoji ZWJ
                    # families stay one unbreakable unit).
                    groups[-1][0] += char
                    groups[-1][1] += width
                    groups[-1][2] = "w"
                else:
                    groups.append([char, 2, "w"])
                zwj_pending = False
            elif groups and groups[-1][2] == "n":
                groups[-1][0] += char
                groups[-1][1] += width
                zwj_pending = False
            else:
                groups.append([char, width, "n"])
                zwj_pending = False
        if not groups:
            # A chunk made only of zero-width characters.
            units.append((chunk, 0, False))
            continue
        groups[0][0] = lead_zero + groups[0][0]
        units.extend((text_, width_, False) for text_, width_, _ in groups)
    return units


class TextWrapTool(Tool):
    """Display-width-aware text wrapping / reflow tool (pure stdlib).

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "text_wrap_tool"
    description: str = (
        "Text wrap tool — pure Python stdlib, no network required, with "
        "east-asian (CJK) display-width awareness. Wrap text to a width "
        "and return the line list (mode='wrap'), reflow to a single "
        "string with a configurable separator (mode='fill'), strip the "
        "common leading whitespace of every line (mode='dedent'), add a "
        "prefix to non-blank lines (mode='indent'), or collapse and "
        "truncate to the width with a '…' placeholder (mode='shorten'). "
        "Wide CJK/fullwidth characters count as two columns, so mixed "
        "CJK and latin text aligns to the requested width."
    )

    MODES: ClassVar[tuple] = ("wrap", "fill", "dedent", "indent", "shorten")

    MIN_WIDTH: ClassVar[int] = 1
    MAX_WIDTH: ClassVar[int] = 200
    DEFAULT_WIDTH: ClassVar[int] = 80

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        width: Any = None,
        break_long_words: Any = None,
        break_on_hyphens: Any = None,
        max_lines: Any = None,
        initial_indent: Any = None,
        subsequent_indent: Any = None,
        separator: Any = None,
        prefix: Any = None,
    ) -> Dict[str, Any]:
        """Run one wrapping / reflow operation.

        Args:
            mode (str): One of ``wrap`` / ``fill`` / ``dedent`` /
                ``indent`` / ``shorten``.
            text (str): The text to process (non-empty string).
            width (int): Display width in columns for the ``wrap``,
                ``fill`` and ``shorten`` modes — 1 to 200, default 80.
                Wide (CJK / fullwidth) characters count as two columns.
            break_long_words (bool): Break words longer than the line
                (default ``True``, matching ``textwrap``).
            break_on_hyphens (bool): Break latin words after hyphens
                (default ``True``, matching ``textwrap``).
            max_lines (int): For the ``wrap`` / ``fill`` modes — emit at
                most this many lines, appending the overflow marker
                ``"… [+N chars]"`` to the last line when content was
                dropped.
            initial_indent (str): Prefix for the first output line of
                the ``wrap`` / ``fill`` modes (default ``""``).
            subsequent_indent (str): Prefix for every following output
                line of the ``wrap`` / ``fill`` modes (default ``""``).
            separator (str): ``fill`` mode only — string joining the
                wrapped lines (default ``"\\n"``).
            prefix (str): ``indent`` mode only — the prefix added to
                every non-blank line.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                — a list of lines for ``wrap``, a string otherwise —
                plus the call context, including ``truncated`` and
                ``dropped_chars`` whenever ``max_lines`` or the
                ``shorten`` placeholder applies).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_width = self._validate_width(width)
        blw = self._validate_flag(break_long_words, "break_long_words")
        boh = self._validate_flag(break_on_hyphens, "break_on_hyphens")
        ml = self._validate_max_lines(max_lines)
        ii = self._validate_indent_str(initial_indent, "initial_indent")
        si = self._validate_indent_str(subsequent_indent, "subsequent_indent")

        if mode in ("wrap", "fill"):
            if _display_width(ii) >= clean_width:
                self._invalid(
                    f"initial_indent display width ({_display_width(ii)}) "
                    f"must be smaller than width ({clean_width})"
                )
            if _display_width(si) >= clean_width:
                self._invalid(
                    f"subsequent_indent display width ({_display_width(si)}) "
                    f"must be smaller than width ({clean_width})"
                )
            lines, truncated, dropped = self._wrap_text(
                clean_text, clean_width, blw, boh, ml, ii, si
            )
            if mode == "wrap":
                return {
                    "mode": "wrap",
                    "width": clean_width,
                    "max_lines": ml,
                    "line_count": len(lines),
                    "truncated": truncated,
                    "dropped_chars": dropped,
                    "result": lines,
                }
            sep = self._validate_separator(separator)
            return {
                "mode": "fill",
                "width": clean_width,
                "max_lines": ml,
                "separator": sep,
                "line_count": len(lines),
                "truncated": truncated,
                "dropped_chars": dropped,
                "result": sep.join(lines),
            }
        if mode == "dedent":
            return {"mode": "dedent", "result": textwrap.dedent(clean_text)}
        if mode == "indent":
            clean_prefix = self._validate_prefix(prefix)
            return {
                "mode": "indent",
                "prefix": clean_prefix,
                "result": textwrap.indent(clean_text, clean_prefix),
            }
        return self._shorten(clean_text, clean_width, blw, boh)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"text_wrap_tool: {message}")

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
        """Validate the ``width`` option (used by wrap/fill/shorten)."""
        if width is None:
            return cls.DEFAULT_WIDTH
        if isinstance(width, bool) or not isinstance(width, int):
            cls._invalid(
                f"width must be an integer between {cls.MIN_WIDTH} and "
                f"{cls.MAX_WIDTH} (got {width!r})"
            )
        if not cls.MIN_WIDTH <= width <= cls.MAX_WIDTH:
            cls._invalid(
                f"width must be between {cls.MIN_WIDTH} and {cls.MAX_WIDTH} "
                f"inclusive (got {width})"
            )
        return width

    @classmethod
    def _validate_flag(cls, flag: Any, name: str) -> bool:
        """Validate a boolean flag such as ``break_long_words``."""
        if flag is None:
            return True
        if not isinstance(flag, bool):
            cls._invalid(f"{name} must be a boolean or None (got {flag!r})")
        return flag

    @classmethod
    def _validate_max_lines(cls, max_lines: Any) -> Optional[int]:
        """Validate the ``max_lines`` option."""
        if max_lines is None:
            return None
        if isinstance(max_lines, bool) or not isinstance(max_lines, int):
            cls._invalid(
                f"max_lines must be a positive integer or None "
                f"(got {max_lines!r})"
            )
        if max_lines < 1:
            cls._invalid(f"max_lines must be >= 1 (got {max_lines})")
        return max_lines

    @classmethod
    def _validate_indent_str(cls, indent: Any, name: str) -> str:
        """Validate the string type and content of an indent option."""
        if indent is None:
            return ""
        if isinstance(indent, bool) or not isinstance(indent, str):
            cls._invalid(f"{name} must be a string or None (got {indent!r})")
        if any(char in indent for char in ("\n", "\r", "\x0b", "\x0c")):
            cls._invalid(
                f"{name} must not contain hard newlines (got {indent!r})"
            )
        return indent

    @classmethod
    def _validate_separator(cls, separator: Any) -> str:
        """Validate the ``fill`` mode line separator."""
        if separator is None:
            return "\n"
        if isinstance(separator, bool) or not isinstance(separator, str):
            cls._invalid(
                f"separator must be a string or None (got {separator!r})"
            )
        if len(separator) > 1_000:
            cls._invalid(
                f"separator exceeds the 1,000-character limit "
                f"(got {len(separator):,} characters)"
            )
        return separator

    @classmethod
    def _validate_prefix(cls, prefix: Any) -> str:
        """Validate the ``indent`` mode prefix."""
        if prefix is None or isinstance(prefix, bool) or not isinstance(prefix, str):
            cls._invalid(f"prefix must be a non-empty string (got {prefix!r})")
        if not prefix:
            cls._invalid("prefix must be a non-empty string (got '')")
        if len(prefix) > 200:
            cls._invalid(
                f"prefix exceeds the 200-character limit "
                f"(got {len(prefix):,} characters)"
            )
        return prefix

    # ------------------------------------------------------------------ #
    # Width-aware wrapping engine
    # ------------------------------------------------------------------ #

    def _wrap_text(
        self,
        text: str,
        width: int,
        break_long_words: bool,
        break_on_hyphens: bool,
        max_lines: Optional[int],
        initial_indent: str,
        subsequent_indent: str,
    ) -> Tuple[List[str], bool, int]:
        """Wrap the whole text (hard newlines included) to lines."""
        # Whitespace munging, in textwrap's order: tabs are expanded
        # first; \r\n and lone \r then become hard newlines (instead of
        # textwrap's space conversion) so line structure is preserved.
        expanded = text.expandtabs(8)
        normalized = expanded.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.replace("\x0b", " ").replace("\x0c", " ")

        lines: List[str] = []
        for hard_line in normalized.split("\n"):
            if not hard_line.strip():
                # Explicit blank (or whitespace-only) line: an empty
                # output line, without any indent.
                lines.append("")
                continue
            units = _build_units(hard_line, break_on_hyphens)
            lines.extend(
                self._wrap_units(
                    units,
                    width,
                    break_long_words,
                    break_on_hyphens,
                    initial_indent,
                    subsequent_indent,
                    lines_already=bool(lines),
                )
            )
        if max_lines is None or len(lines) <= max_lines:
            return lines, False, 0
        return self._apply_max_lines(lines, max_lines, width)

    def _wrap_units(
        self,
        units: List[_Unit],
        width: int,
        break_long_words: bool,
        break_on_hyphens: bool,
        initial_indent: str,
        subsequent_indent: str,
        lines_already: bool,
    ) -> List[str]:
        """Greedy-wrap one hard line's units (mirrors textwrap's loop).

        ``lines_already`` tells whether previous hard lines already
        produced output, which decides both which indent applies (the
        very first output line of the whole text takes
        ``initial_indent``, every other line ``subsequent_indent``)
        and whether leading whitespace is dropped (``drop_whitespace``
        only keeps it at the very beginning of the text).
        """
        lines: List[str] = []
        initial_width = _display_width(initial_indent)
        subsequent_width = _display_width(subsequent_indent)
        pos = 0
        total = len(units)

        while pos < total:
            at_text_start = not lines and not lines_already
            if at_text_start:
                indent, indent_width = initial_indent, initial_width
            else:
                indent, indent_width = subsequent_indent, subsequent_width
                # Drop leading whitespace chunks (textwrap keeps them
                # only at the very beginning of the text).
                while pos < total and units[pos][2]:
                    pos += 1
                if pos >= total:
                    break
            avail = width - indent_width  # >= 1: indents are validated < width

            cur: List[str] = []
            cur_w = 0
            while pos < total:
                unit_text, unit_w, _ = units[pos]
                if cur_w + unit_w <= avail:
                    cur.append(unit_text)
                    cur_w += unit_w
                    pos += 1
                else:
                    break

            # The next unit is too wide for ANY line of this width.
            if pos < total and units[pos][1] > avail:
                unit_text, unit_w, is_ws = units[pos]
                space_left = avail - cur_w
                if space_left < 1:
                    # Nothing more fits.  textwrap appends an empty
                    # fragment in this case, which shields a preceding
                    # whitespace chunk from the trailing drop below
                    # (reproduced here for byte-identical output);
                    # otherwise the line just closes and the next one
                    # starts fresh, so progress is guaranteed either way.
                    if break_long_words:
                        cur.append("")
                elif break_long_words:
                    end = space_left
                    if (
                        break_on_hyphens
                        and not is_ws
                        and len(unit_text) == unit_w
                    ):
                        # Pure-narrow chunk: prefer breaking after the
                        # last hyphen that fits, exactly like
                        # textwrap._handle_long_word.
                        hyphen = unit_text.rfind("-", 0, space_left)
                        if hyphen > 0 and any(
                            char != "-" for char in unit_text[:hyphen]
                        ):
                            end = hyphen + 1
                    head, head_w = _slice_by_width(unit_text, end)
                    if not head:
                        if cur:
                            # Close the line; retry on a fresh one.
                            pass
                        else:
                            # A single wide unit cannot fit the line at
                            # all — take it whole (overlong by design).
                            head, head_w = unit_text, unit_w
                    if head:
                        cur.append(head)
                        cur_w += head_w
                        remainder = unit_text[len(head):]
                        units[pos] = (
                            remainder,
                            unit_w - head_w,
                            is_ws,
                        )
                elif not cur:
                    # break_long_words disabled: keep the overlong word
                    # intact on a line of its own.
                    cur.append(unit_text)
                    cur_w += unit_w
                    pos += 1

            # Drop a trailing whitespace chunk.
            if cur and not cur[-1].strip():
                cur_w -= _display_width(cur[-1])
                cur.pop()

            if cur:
                lines.append(indent + "".join(cur))
        return lines

    # ------------------------------------------------------------------ #
    # max_lines truncation with the "… [+N chars]" overflow marker
    # ------------------------------------------------------------------ #

    @classmethod
    def _apply_max_lines(
        cls, lines: List[str], max_lines: int, width: int
    ) -> Tuple[List[str], bool, int]:
        """Truncate to ``max_lines`` lines and fit the overflow marker.

        The dropped-character count *N* is the number of content
        characters removed: the stripped content of every dropped line
        plus the length of every word moved off the last kept line to
        make room for the marker (whitespace separators and line
        indents are not counted).  When even an emptied last line
        cannot hold the marker it is emitted anyway, exceeding
        ``width`` rather than looping or hiding the truncation.
        """
        kept = lines[:max_lines]
        dropped_chars = sum(len(line.strip()) for line in lines[max_lines:])
        truncated = True
        if dropped_chars == 0:
            # Only blank lines were dropped — nothing to mark.
            return kept, truncated, 0

        marker = f"{_OVERFLOW_PREFIX}{dropped_chars}{_OVERFLOW_SUFFIX}"
        while True:
            base = kept[-1] if kept else ""
            content = base.rstrip()
            if not content.strip():
                # Blank (or emptied) last line: the marker stands alone.
                if kept:
                    kept[-1] = marker
                else:
                    kept = [marker]
                break
            if _display_width(content) + 1 + _display_width(marker) <= width:
                kept[-1] = content + " " + marker
                break
            popped = cls._pop_last_word(content)
            if popped is None:
                # Cannot shrink any further — emit the marker anyway so
                # the truncation stays visible (line may exceed width).
                kept[-1] = content + " " + marker
                break
            head, word = popped
            kept[-1] = head
            dropped_chars += len(word)
            marker = f"{_OVERFLOW_PREFIX}{dropped_chars}{_OVERFLOW_SUFFIX}"
        return kept, truncated, dropped_chars

    @staticmethod
    def _pop_last_word(line: str) -> Optional[Tuple[str, str]]:
        """Split off the last space-delimited word of a line.

        Returns ``(head, word)`` where ``head`` keeps the leading
        whitespace (indent) and everything before the final word, or
        ``None`` when the line holds a single unsplittable word — in
        that case the caller drops the whole line content.
        """
        stripped = line.rstrip()
        lead_len = len(stripped) - len(stripped.lstrip())
        lead = stripped[:lead_len]
        core = stripped[lead_len:]
        if not core:
            return None
        if " " in core:
            head, _, word = core.rpartition(" ")
            return lead + head, word
        return "", core

    # ------------------------------------------------------------------ #
    # shorten mode
    # ------------------------------------------------------------------ #

    def _shorten(
        self, text: str, width: int, break_long_words: bool, break_on_hyphens: bool
    ) -> Dict[str, Any]:
        """Collapse whitespace, then truncate to ``width`` with '…'.

        Mirrors ``textwrap.shorten`` (which normalizes with
        ``" ".join(text.strip().split())`` and fills a single line with
        the placeholder appended — sliced word fragments never
        survive) but measures display width, so CJK content truncates
        in terminal columns.  ``break_long_words`` /
        ``break_on_hyphens`` only shape which words are considered:
        whole words that fit are always preferred, and when even the
        first word plus the placeholder does not fit, the result is
        the placeholder alone.
        """
        collapsed = " ".join(text.strip().split())
        if _display_width(collapsed) <= width:
            return {
                "mode": "shorten",
                "width": width,
                "truncated": False,
                "dropped_chars": 0,
                "result": collapsed,
            }
        units = _build_units(collapsed, break_on_hyphens)
        placeholder_w = _display_width(_SHORTEN_PLACEHOLDER)
        cur: List[str] = []
        cur_w = 0
        pos = 0
        while pos < len(units):
            unit_text, unit_w, _ = units[pos]
            if cur_w + unit_w <= width:
                cur.append(unit_text)
                cur_w += unit_w
                pos += 1
            else:
                break
        if pos >= len(units):
            # Defensive: the pre-check above already returned when the
            # whole collapsed text fits, so this branch is unreachable.
            return {
                "mode": "shorten",
                "width": width,
                "truncated": False,
                "dropped_chars": 0,
                "result": collapsed,
            }
        # Pop words until the placeholder fits (mirroring textwrap's
        # max_lines=1 commit logic: fragments never survive, trailing
        # whitespace goes first).
        while cur:
            if not cur[-1].strip() or cur_w + placeholder_w > width:
                removed = cur.pop()
                cur_w -= _display_width(removed)
            else:
                break
        if cur:
            kept = "".join(cur)
            result = kept + _SHORTEN_PLACEHOLDER
            dropped = len(collapsed) - len(kept)
        else:
            result = _SHORTEN_PLACEHOLDER
            dropped = len(collapsed)
        return {
            "mode": "shorten",
            "width": width,
            "truncated": True,
            "dropped_chars": dropped,
            "result": result,
        }
