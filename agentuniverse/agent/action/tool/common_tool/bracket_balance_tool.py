#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: bracket_balance_tool.py

"""Bracket / quote balance checking tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency delimiter checker
agents can call before parsing, templating or forwarding text: it
reports the precise position of the first bracket error, lists every
unbalanced position, repairs simple imbalances and profiles nesting.

Six pair types are tracked as first-class citizens — ``()``, ``[]``,
``{}`` and the CJK full-width brackets ``（）`` / ``【】`` / ``《》``
(each full-width pair is its own type; it never matches an ASCII
bracket). ASCII ``<>`` is tracked only when the ``angle_brackets``
option is enabled, because in plain prose ``<`` and ``>`` are usually
comparison or punctuation characters rather than delimiters. When the
option is on, an inside-word *generics heuristic* applies (the
``a<b>c`` case): ``<`` counts as an opener only when the previous
character is a word character (``List<Integer>`` yes, ``a < b`` no),
and ``>`` counts as a closer only when the character before it is a
word character (or ``>`` itself, for nested ``>>``) *and* the innermost
open bracket is a ``<`` — so the comparison in ``f(x > 2)`` stays
inert. The heuristic is documented, approximate, and OFF by default.

Quotes are handled by a string-aware mode (``string_aware``, ON by
default): ``'``, ``"`` and `` ` `` each open a quoted span that is
closed only by the same character, and a backslash inside a span
escapes the next character (``\\'`` does not close). Brackets inside a
quoted span are INERT — they are not counted and never match. A span
left open at end of text is reported as an ``unterminated_string``
error; closing a span with a different quote character does not close
it, so mismatched closing quotes surface as errors instead of
silently corrupting the scan. Prose containing apostrophes
(``don't``) can therefore report false strings — set
``string_aware=False`` to count every bracket regardless of quotes.

Four modes:

* ``check`` — is the text balanced? Returns ``balanced``, the precise
  ``first_error`` (position, line, col, kind ``unmatched_open`` /
  ``unmatched_close`` / ``mismatched_pair`` / ``unterminated_string``,
  plus ``expected`` / ``found`` characters where applicable), the
  per-type open/close counts and the maximum stack depth. The first
  error is the first one encountered while scanning (a mismatched or
  orphan closer is reported before the unmatched openers that are only
  detected at end of text).
* ``locate`` — every unbalanced position (capped at 100, sorted by
  position) with line/col, the total count and a ``truncated`` flag.
* ``fix`` — repair simple imbalances. ``fix_modes`` selects the
  repairs: ``drop_orphans`` removes unmatched / mismatched closers,
  ``append_missing_closers`` appends the closers still missing at end
  of text (innermost first). Drops are applied before appends, drop
  positions refer to the original text, and the result reports the
  applied fixes and whether the repaired text is now balanced.
* ``stats`` — per-type open/close counts and maximum nesting depth
  per type, plus overall totals.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty text, unknown mode or fix
mode, ``fix_modes`` outside the ``fix`` mode, non-boolean options,
text over 100,000 characters) raise a ``ValueError``, mirroring the
other common tools. Unbalanced text is *not* an input error — it is
the tool's normal, structured output.
"""

from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class BracketBalanceTool(Tool):
    """Bracket / quote balance checker built purely on the stdlib.

    Attributes:
        max_text_chars (int): Upper bound on the ``text`` input length;
            longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "bracket_balance_tool"
    description: str = (
        "Bracket balance tool — pure Python stdlib, no network required. "
        "Check whether text has balanced brackets and quotes with the "
        "precise first-error position (mode='check'), list every "
        "unbalanced position capped at 100 (mode='locate'), repair "
        "simple imbalances by dropping orphan closers and appending "
        "missing closers (mode='fix'), or profile per-type counts and "
        "nesting depth (mode='stats'). Tracks (), [], {}, the CJK "
        "full-width （）【】《》 pairs, and <> behind an inside-word "
        "generics heuristic (angle_brackets option, off by default). "
        "Quotes make brackets inside them inert (string_aware option, "
        "on by default)."
    )

    MODES: ClassVar[tuple] = ("check", "locate", "fix", "stats")
    FIX_MODES: ClassVar[tuple] = ("append_missing_closers", "drop_orphans")
    # Canonical application order: drops run before appends so the
    # appended closers match the brackets that survive the drops.
    FIX_ORDER: ClassVar[tuple] = ("drop_orphans", "append_missing_closers")
    LOCATE_CAP: ClassVar[int] = 100
    # Ordered registry: (type key, open char, close char). The ASCII
    # angle pair is only active when the angle_brackets option is on;
    # the three CJK full-width pairs are always active and never match
    # an ASCII bracket.
    PAIR_TYPES: ClassVar[Tuple[Tuple[str, str, str], ...]] = (
        ("()", "(", ")"),
        ("[]", "[", "]"),
        ("{}", "{", "}"),
        ("<>", "<", ">"),
        ("（）", "（", "）"),
        ("【】", "【", "】"),
        ("《》", "《", "》"),
    )
    ANGLE_KEY: ClassVar[str] = "<>"
    QUOTE_CHARS: ClassVar[Tuple[str, ...]] = ("'", '"', "`")

    max_text_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        text: Any = None,
        string_aware: Any = None,
        angle_brackets: Any = None,
        fix_modes: Any = None,
    ) -> Dict[str, Any]:
        """Run one bracket balance operation.

        Args:
            mode (str): One of ``check`` / ``locate`` / ``fix`` /
                ``stats``.
            text (str): The text to scan (1 .. 100,000 characters).
            string_aware (bool): When True (default) ``'`` / ``"`` /
                backtick open quoted spans that make brackets inside
                them inert; a backslash inside a span escapes the next
                character. When False every bracket counts and quote
                characters are ordinary text.
            angle_brackets (bool): When False (default) ASCII ``<`` and
                ``>`` are ordinary text. When True they are tracked with
                the documented inside-word generics heuristic
                (``a<b>c``).
            fix_modes (list[str]): Fix mode only — subset of
                ``append_missing_closers`` (append the closers still
                missing at end of text, innermost first) and
                ``drop_orphans`` (remove unmatched / mismatched
                closers). Defaults to both; drops are applied before
                appends.

        Returns:
            Dict[str, Any]: The operation result (see the mode
                descriptions in the module docstring). Unbalanced text
                is reported structurally, never as an exception.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_text = self._validate_text(text)
        clean_string_aware = self._validate_flag(
            string_aware, "string_aware", default=True
        )
        clean_angle = self._validate_flag(
            angle_brackets, "angle_brackets", default=False
        )
        clean_fix_modes = self._validate_fix_modes(fix_modes, mode)

        scan = self._scan(clean_text, clean_string_aware, clean_angle)

        if mode == "check":
            return self._result_check(
                clean_text, clean_string_aware, clean_angle, scan
            )
        if mode == "locate":
            return self._result_locate(
                clean_text, clean_string_aware, clean_angle, scan
            )
        if mode == "fix":
            return self._result_fix(
                clean_text,
                clean_string_aware,
                clean_angle,
                scan,
                clean_fix_modes,
            )
        return self._result_stats(
            clean_text, clean_string_aware, clean_angle, scan
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"bracket_balance_tool: {message}")

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
    def _validate_flag(cls, value: Any, name: str, default: bool) -> bool:
        """Validate a boolean option, accepting ``None`` for the default."""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean or None (got {value!r})")

    @classmethod
    def _validate_fix_modes(cls, fix_modes: Any, mode: str) -> Tuple[str, ...]:
        """Validate the fix-mode ``fix_modes`` selector."""
        if fix_modes is None:
            return cls.FIX_ORDER
        if mode != "fix":
            cls._invalid(
                "fix_modes is only valid for mode='fix' "
                f"(got mode={mode!r})"
            )
        if isinstance(fix_modes, (str, bytes)) or not isinstance(
            fix_modes, (list, tuple)
        ):
            cls._invalid(
                "fix_modes must be a list containing any of: "
                f"{', '.join(cls.FIX_MODES)} (got {fix_modes!r})"
            )
        cleaned: List[str] = []
        for entry in fix_modes:
            if entry not in cls.FIX_MODES:
                cls._invalid(
                    "fix_modes entries must be any of: "
                    f"{', '.join(cls.FIX_MODES)} (got {entry!r})"
                )
            if entry not in cleaned:
                cleaned.append(entry)
        return tuple(
            entry for entry in cls.FIX_ORDER if entry in cleaned
        )

    # ------------------------------------------------------------------ #
    # Core scanner (single pass, shared by every mode)
    # ------------------------------------------------------------------ #

    def _scan(
        self, text: str, string_aware: bool, angle_brackets: bool
    ) -> Dict[str, Any]:
        """Scan ``text`` once and collect every structural fact.

        Returns a dict with the error events in scan-encounter order
        (``events``), the openers still on the stack at end of text
        (``stack``, innermost last), the per-type counts and nesting
        maxima (``per_type``), the overall totals (``overall``) and the
        maximum stack depth (``stack_depth_max``).
        """
        open_to_close: Dict[str, str] = {}
        open_to_key: Dict[str, str] = {}
        close_to_open: Dict[str, str] = {}
        active_keys: List[str] = []
        for key, open_char, close_char in self.PAIR_TYPES:
            if key == self.ANGLE_KEY and not angle_brackets:
                continue
            open_to_close[open_char] = close_char
            open_to_key[open_char] = key
            close_to_open[close_char] = key
            active_keys.append(key)

        per_type: Dict[str, Dict[str, int]] = {
            key: {"open": 0, "close": 0, "max_depth": 0}
            for key in active_keys
        }
        depth_now = {key: 0 for key in active_keys}
        overall = {"open": 0, "close": 0, "max_depth": 0}

        events: List[Dict[str, Any]] = []
        stack: List[Tuple[str, str, int]] = []  # (type key, close char, position)
        in_string = False
        quote_char = ""
        quote_position = 0

        index = 0
        length = len(text)
        while index < length:
            char = text[index]
            if in_string:
                if char == "\\":
                    index += 2  # escaped character stays inert
                    continue
                if char == quote_char:
                    in_string = False
                index += 1
                continue
            if string_aware and char in self.QUOTE_CHARS:
                in_string = True
                quote_char = char
                quote_position = index
                index += 1
                continue

            is_opener = char in open_to_close
            is_closer = char in close_to_open

            # Inside-word generics heuristic for ASCII angle brackets:
            # "<" opens only right after a word character (never at
            # start of text); ">" closes only after a word character
            # (or ">" itself, for nested ">>") and only when the
            # innermost open bracket is itself a "<".
            if is_opener and char == "<":
                previous = text[index - 1] if index > 0 else None
                if previous is None or not (
                    previous.isalnum() or previous == "_"
                ):
                    is_opener = False
            if is_closer and char == ">" and (
                not stack or stack[-1][0] != self.ANGLE_KEY
            ):
                is_closer = False
            if is_closer and char == ">":
                previous = text[index - 1] if index > 0 else None
                if previous is None or not (
                    previous.isalnum() or previous in ("_", ">")
                ):
                    is_closer = False

            if is_opener:
                key = open_to_key[char]
                per_type[key]["open"] += 1
                overall["open"] += 1
                depth_now[key] += 1
                per_type[key]["max_depth"] = max(
                    per_type[key]["max_depth"], depth_now[key]
                )
                stack.append((key, open_to_close[char], index))
                overall["max_depth"] = max(overall["max_depth"], len(stack))
                index += 1
                continue

            if is_closer:
                key = close_to_open[char]
                per_type[key]["close"] += 1
                overall["close"] += 1
                if stack and stack[-1][0] == key:
                    stack.pop()
                    depth_now[key] -= 1
                elif stack:
                    events.append(
                        self._event(
                            text,
                            index,
                            "mismatched_pair",
                            expected=stack[-1][1],
                            found=char,
                        )
                    )
                else:
                    events.append(
                        self._event(
                            text, index, "unmatched_close", found=char
                        )
                    )
                index += 1
                continue

            index += 1

        if in_string:
            events.append(
                self._event(
                    text,
                    quote_position,
                    "unterminated_string",
                    quote=quote_char,
                )
            )
        # Unmatched openers surface at end of text, innermost first;
        # they keep their original opening position for reporting.
        for key, close_char, position in reversed(stack):
            events.append(
                self._event(
                    text, position, "unmatched_open", expected=close_char
                )
            )
        return {
            "events": events,
            "stack": stack,
            "per_type": per_type,
            "overall": overall,
            "stack_depth_max": overall["max_depth"],
        }

    @staticmethod
    def _event(
        text: str,
        position: int,
        kind: str,
        expected: Any = None,
        found: Any = None,
        quote: Any = None,
    ) -> Dict[str, Any]:
        """Build one error event with 1-based line / column data."""
        line = text.count("\n", 0, position) + 1
        last_newline = text.rfind("\n", 0, position)
        column = (
            position - last_newline if last_newline >= 0 else position + 1
        )
        event: Dict[str, Any] = {
            "position": position,
            "line": line,
            "col": column,
            "kind": kind,
        }
        if expected is not None:
            event["expected"] = expected
        if found is not None:
            event["found"] = found
        if quote is not None:
            event["quote"] = quote
        return event

    # ------------------------------------------------------------------ #
    # Mode result builders
    # ------------------------------------------------------------------ #

    @classmethod
    def _result_check(
        cls,
        text: str,
        string_aware: bool,
        angle_brackets: bool,
        scan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the ``check`` result payload."""
        events = scan["events"]
        return {
            "mode": "check",
            "string_aware": string_aware,
            "angle_brackets": angle_brackets,
            "balanced": not events,
            "error_count": len(events),
            "first_error": dict(events[0]) if events else None,
            "per_type": {
                key: {"open": counts["open"], "close": counts["close"]}
                for key, counts in scan["per_type"].items()
            },
            "stack_depth_max": scan["stack_depth_max"],
        }

    @classmethod
    def _result_locate(
        cls,
        text: str,
        string_aware: bool,
        angle_brackets: bool,
        scan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the ``locate`` result payload (positions sorted, capped)."""
        events = scan["events"]
        ordered = sorted(events, key=lambda event: event["position"])
        capped = ordered[: cls.LOCATE_CAP]
        return {
            "mode": "locate",
            "string_aware": string_aware,
            "angle_brackets": angle_brackets,
            "balanced": not events,
            "total": len(events),
            "cap": cls.LOCATE_CAP,
            "truncated": len(events) > cls.LOCATE_CAP,
            "positions": capped,
        }

    def _result_fix(
        self,
        text: str,
        string_aware: bool,
        angle_brackets: bool,
        scan: Dict[str, Any],
        fix_modes: Tuple[str, ...],
    ) -> Dict[str, Any]:
        """Build the ``fix`` result payload.

        ``drop_orphans`` removes the closers reported as
        ``unmatched_close`` or ``mismatched_pair`` (positions refer to
        the original text); ``append_missing_closers`` appends the
        closers for the openers left on the stack, innermost first.
        Drops run before appends.
        """
        drop_positions = {
            event["position"]
            for event in scan["events"]
            if event["kind"] in ("unmatched_close", "mismatched_pair")
        }
        builder: List[str] = []
        applied: List[Dict[str, Any]] = []
        for position, char in enumerate(text):
            if position in drop_positions and "drop_orphans" in fix_modes:
                applied.append(
                    {
                        "action": "dropped_closer",
                        "position": position,
                        "line": self._line_of(text, position),
                        "col": self._col_of(text, position),
                        "char": char,
                    }
                )
                continue
            builder.append(char)
        if "append_missing_closers" in fix_modes:
            for _, close_char, _ in reversed(scan["stack"]):
                applied.append(
                    {
                        "action": "appended_closer",
                        "position": len(builder),
                        "char": close_char,
                    }
                )
                builder.append(close_char)
        fixed_text = "".join(builder)
        recheck = self._scan(fixed_text, string_aware, angle_brackets)
        remaining = len(recheck["events"])
        return {
            "mode": "fix",
            "fix_modes": list(fix_modes),
            "fixed_text": fixed_text,
            "applied": applied,
            "applied_count": len(applied),
            "balanced_after_fix": remaining == 0,
            "remaining_error_count": remaining,
        }

    @classmethod
    def _result_stats(
        cls,
        text: str,
        string_aware: bool,
        angle_brackets: bool,
        scan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the ``stats`` result payload."""
        return {
            "mode": "stats",
            "string_aware": string_aware,
            "angle_brackets": angle_brackets,
            "chars": len(text),
            "lines": text.count("\n") + 1,
            "per_type": {
                key: dict(counts)
                for key, counts in scan["per_type"].items()
            },
            "overall": dict(scan["overall"]),
        }

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _line_of(text: str, position: int) -> int:
        """1-based line number of a character position."""
        return text.count("\n", 0, position) + 1

    @staticmethod
    def _col_of(text: str, position: int) -> int:
        """1-based column (in characters) of a character position."""
        last_newline = text.rfind("\n", 0, position)
        return (
            position - last_newline if last_newline >= 0 else position + 1
        )
