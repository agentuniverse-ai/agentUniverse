#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: join_tool.py

"""List joining tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency utility for the
humble-but-ubiquitous job of turning a list into prose: joining
items with a delimiter, Oxford-comma conjunctions, numbered outlines
and bullet lists.

The tool is a thin, strictly-validated façade over built-in string
operations and supports four modes:

* ``join`` — join a list of items with a ``delimiter`` (default
  ``", "``). ``style`` selects the conjunction treatment:
  ``plain`` (``a, b, c``), ``oxford`` (``a, b, and c``; two items
  give ``a and b`` without a comma — the standard short form —
  and a single item is returned unchanged), ``and``
  (``a and b`` / ``a, b and c``, documented *without* the final
  comma) and ``or`` (``a or b`` / ``a, b, or c``). Empty-string
  items are kept by default; ``drop_empty=True`` drops them and
  reports how many were dropped.
* ``join_pairs`` — join a list of ``[key, value]`` pairs (two-item
  lists/tuples) or single-key ``{key: value}`` dicts, formatting
  each pair as ``key + kv_sep + value`` (``kv_sep`` defaults to
  ``=``) and joining the formatted pairs with ``item_delim``
  (default ``", "``): ``a=1, b=2``.
* ``numbered`` — prefix running numbers, ``1. a`` / ``1) a`` per
  ``number_format`` (``dot`` / ``paren``), starting at ``start``
  (default 1), one item per line.
* ``bullet`` — prefix every item with ``bullet`` (default ``-``),
  one item per line.

Items must be strings, or ints/floats/bools, which are coerced with
one documented rule: ``str(value)`` for numbers, ``"true"`` /
``"false"`` for booleans (JSON style), non-finite floats rejected.

An empty item list yields a structured note (``(no items to join)``)
by default, or an empty string with ``empty_as="empty"``; the option
applies to every mode. All modes cap the input at 10,000 items and
the separators at 10,000 characters.

Everything is deterministic — no randomness, no time dependence, no
network. Input validation is strict and happens before any work:
malformed parameters (unknown mode, non-list ``items``, non-scalar
items, unknown ``style`` / ``number_format`` / ``empty_as`` values,
wrong-typed or over-long separators, an empty ``delimiter`` when two
or more items remain, an empty ``kv_sep`` / ``item_delim`` /
``bullet``, out-of-bounds ``start``, mode-specific options used with
the wrong mode, more than 10,000 items) raise a ``ValueError``
mirroring the other common tools. Joining itself never fails on
content, so no error payloads are needed.
"""

# Strict validation raises ValueError with a descriptive message.
# ruff: noqa: TRY003

import math
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Result returned for an empty item list when empty_as="note".
EMPTY_NOTE = "(no items to join)"


class JoinTool(Tool):
    """List joining tool built purely on the stdlib.

    Attributes:
        max_items (int): Upper bound on the number of input items;
            larger inputs are rejected before any work.
        max_sep_chars (int): Upper bound on the length of every
            separator-style option (delimiter, kv_sep, item_delim).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "join_tool"
    description: str = (
        "List joining tool — pure Python stdlib, no network required. "
        "Join a list of items with a delimiter (default ', ') in plain, "
        "oxford ('a, b, and c'; two items give 'a and b'), and ('a, b "
        "and c', no final comma) or or ('a, b, or c') style, keeping "
        "empty-string items by default or dropping them (mode='join'); "
        "join [key, value] pairs or single-key dicts as 'a=1, b=2' with "
        "custom kv_sep and item_delim (mode='join_pairs'); prefix "
        "running numbers as '1. a' / '1) a' with a custom start "
        "(mode='numbered'); or prefix a bullet character (default '-') "
        "(mode='bullet'). Strings, ints, floats and bools are coerced "
        "with one documented rule; an empty list yields a structured "
        "note or '' per option; inputs are capped and strictly "
        "validated."
    )

    MODES: ClassVar[tuple] = ("join", "join_pairs", "numbered", "bullet")
    STYLES: ClassVar[tuple] = ("plain", "oxford", "and", "or")
    FORMATS: ClassVar[tuple] = ("dot", "paren")
    EMPTY_RESULTS: ClassVar[tuple] = ("note", "empty")

    max_items: int = 10_000
    max_sep_chars: int = 10_000
    max_bullet_chars: int = 16

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        items: Any = None,
        delimiter: Any = None,
        style: Any = None,
        drop_empty: Any = None,
        empty_as: Any = None,
        kv_sep: Any = None,
        item_delim: Any = None,
        number_format: Any = None,
        start: Any = None,
        bullet: Any = None,
    ) -> dict[str, Any]:
        """Run one list-joining operation.

        Args:
            mode (str): One of ``join`` / ``join_pairs`` /
                ``numbered`` / ``bullet``.
            items (list): The input items. Required for every mode;
                a list or tuple of strings, ints, floats or bools for
                ``join`` / ``numbered`` / ``bullet``, and a list of
                two-item lists/tuples or single-key dicts for
                ``join_pairs``. Non-string scalars are coerced with
                one documented rule: ``str(value)`` for ints and
                finite floats, ``"true"`` / ``"false"`` for booleans.
            delimiter (str): Join mode only — separator between
                items (default ``", "``); must be non-empty whenever
                two or more items remain after ``drop_empty``.
            style (str): Join mode only — ``plain`` (default),
                ``oxford`` (``a, b, and c``; two items give
                ``a and b`` without a comma), ``and`` (``a and b`` /
                ``a, b and c``, documented without the final comma)
                or ``or`` (``a or b`` / ``a, b, or c``).
            drop_empty (bool): Join mode only — drop empty-string
                items before joining and report how many were
                dropped; by default empty strings are kept.
            empty_as (str): Every mode — what to return when the
                (possibly post-``drop_empty``) item list is empty:
                ``note`` (default, the structured note
                ``(no items to join)``) or ``empty`` (an empty
                string).
            kv_sep (str): join_pairs mode only — separator between
                each key and value (default ``=``; always non-empty).
            item_delim (str): join_pairs mode only — separator
                between formatted pairs (default ``", "``).
            number_format (str): Numbered mode only — ``dot``
                (``1. a``) or ``paren`` (``1) a``).
            start (int): Numbered mode only — first number
                (default 1; 0-999999).
            bullet (str): Bullet mode only — the bullet prefix
                (default ``-``; non-empty, at most 16 characters).

        Returns:
            Dict[str, Any]: The join result — always the joined
            ``result`` string, the ``mode``, the ``input_items`` and
            ``output_items`` counts, plus the mode-specific options
            (join: ``style`` / ``delimiter`` / ``drop_empty`` /
            ``items_dropped``; join_pairs: ``kv_sep`` /
            ``item_delim``; numbered: ``number_format`` / ``start``;
            bullet: ``bullet``).

        Raises:
            ValueError: If any parameter is malformed (before any
                processing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        self._validate_option_modes(
            mode,
            delimiter=delimiter,
            style=style,
            drop_empty=drop_empty,
            kv_sep=kv_sep,
            item_delim=item_delim,
            number_format=number_format,
            start=start,
            bullet=bullet,
        )
        clean_empty_as = self._validate_empty_as(empty_as)
        strings = self._validate_items(mode, items)
        context: dict[str, Any] = {"mode": mode, "input_items": len(strings)}
        if mode == "join":
            return self._run_join(
                strings, delimiter, style, drop_empty, clean_empty_as, context
            )
        if mode == "join_pairs":
            return self._run_join_pairs(
                strings, kv_sep, item_delim, clean_empty_as, context
            )
        if mode == "numbered":
            return self._run_numbered(
                strings, number_format, start, clean_empty_as, context
            )
        return self._run_bullet(strings, bullet, clean_empty_as, context)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any processing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"join_tool: {message}")

    # Options that only some modes understand, mapped to the modes
    # that accept them; every other mode must omit them (None).
    # items and empty_as are valid in every mode and are validated
    # separately.
    _OPTION_MODES: ClassVar[dict] = {
        "delimiter": ("join",),
        "style": ("join",),
        "drop_empty": ("join",),
        "kv_sep": ("join_pairs",),
        "item_delim": ("join_pairs",),
        "number_format": ("numbered",),
        "start": ("numbered",),
        "bullet": ("bullet",),
    }

    @classmethod
    def _validate_option_modes(cls, mode: str, **options: Any) -> None:
        """Reject mode-specific options passed with the wrong mode.

        Silently ignoring ``style`` in the ``bullet`` mode (or a
        mistyped ``style=1`` there) would hide caller mistakes, so an
        option that only some modes understand must be omitted
        (``None``) everywhere else — mirroring the other common tools.
        """
        for name, value in options.items():
            if value is None:
                continue
            allowed = cls._OPTION_MODES[name]
            if mode not in allowed:
                modes = "/".join(repr(m) for m in allowed)
                noun = "modes" if len(allowed) > 1 else "mode"
                cls._invalid(
                    f"{name} is only valid in the {modes} {noun} "
                    f"(got {name}={value!r} with mode={mode!r})"
                )

    @classmethod
    def _validate_empty_as(cls, empty_as: Any) -> str:
        """Validate the empty-input selector (valid in every mode)."""
        if empty_as is None:
            return "note"
        if empty_as not in cls.EMPTY_RESULTS:
            cls._invalid(
                "empty_as must be one of: "
                f"{', '.join(cls.EMPTY_RESULTS)} (got {empty_as!r})"
            )
        return empty_as

    @classmethod
    def _coerce_scalar(cls, value: Any, name: str) -> str:
        """Coerce one item with the documented scalar rule.

        Strings pass through unchanged; booleans become ``"true"`` /
        ``"false"`` (JSON style, checked before ints because ``bool``
        subclasses ``int``); ints and finite floats become
        ``str(value)``. Everything else — including ``None``, bytes,
        lists and dicts — is rejected.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            if not math.isfinite(value):
                cls._invalid(
                    f"{name} must be a finite float (got {value!r})"
                )
            return str(value)
        cls._invalid(
            f"{name} must be a string, int, float or bool (got {value!r})"
        )

    def _validate_items(self, mode: str, items: Any) -> list:
        """Validate ``items`` and coerce every entry to a string.

        For ``join`` / ``numbered`` / ``bullet`` every element goes
        through the scalar rule and a list of strings is returned;
        for ``join_pairs`` every element must be a two-item
        list/tuple or a single-key dict, and a list of
        ``(key, value)`` string tuples is returned for the runner to
        format with the kv separator.
        """
        if items is None or isinstance(items, (str, bytes, dict)) or not (
            isinstance(items, (list, tuple))
        ):
            self._invalid(f"items must be a list (got {items!r})")
        if len(items) > self.max_items:
            self._invalid(
                f"items exceeds the {self.max_items:,}-item limit "
                f"(got {len(items):,} items)"
            )
        if mode == "join_pairs":
            pairs: list[tuple[str, str]] = []
            for index, element in enumerate(items):
                pairs.append(self._coerce_pair(element, index))
            return pairs
        return [self._coerce_scalar(item, "items entry") for item in items]

    @classmethod
    def _coerce_pair(cls, element: Any, index: int) -> tuple[str, str]:
        """Validate and coerce one join_pairs element.

        Accepts a two-item list/tuple (``["a", 1]``) or a single-key
        dict (``{"a": 1}``); keys and values follow the same scalar
        rule as plain items.
        """
        if isinstance(element, dict):
            if len(element) != 1:
                cls._invalid(
                    f"items[{index}] must be a single-key dict "
                    f"(got {len(element)} keys)"
                )
            key, value = next(iter(element.items()))
        elif isinstance(element, (list, tuple)):
            if len(element) != 2:
                cls._invalid(
                    f"items[{index}] must be a [key, value] pair "
                    f"(got {len(element)} elements)"
                )
            key, value = element
        else:
            cls._invalid(
                f"items[{index}] must be a [key, value] pair or a "
                f"single-key dict (got {element!r})"
            )
        return (
            cls._coerce_scalar(key, f"items[{index}] key"),
            cls._coerce_scalar(value, f"items[{index}] value"),
        )

    def _validate_separator(
        self, value: Any, name: str, default: str, allow_empty: bool = False
    ) -> str:
        """Validate a separator option (``None`` means ``default``).

        Separators must be strings of at most ``max_sep_chars``
        characters; the empty string is rejected unless
        ``allow_empty`` is set (the join delimiter may be empty when
        at most one item will be joined).
        """
        if value is None:
            return default
        if not isinstance(value, str):
            self._invalid(f"{name} must be a string (got {value!r})")
        if not value and not allow_empty:
            self._invalid(f"{name} must be a non-empty string (got '')")
        if len(value) > self.max_sep_chars:
            self._invalid(
                f"{name} exceeds the {self.max_sep_chars:,}-character "
                f"limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_flag(cls, value: Any, name: str) -> bool:
        """Validate a boolean option (``None`` means ``False``)."""
        if value is None:
            return False
        if not isinstance(value, bool):
            cls._invalid(f"{name} must be a boolean or omitted (got {value!r})")
        return value

    @classmethod
    def _validate_count(
        cls, value: Any, name: str, minimum: int, maximum: int, default: int
    ) -> int:
        """Validate an integer option (``None`` means ``default``).

        Accepts real integers and pure ASCII digit strings (so callers
        may pass ``start="5"``); booleans, floats and anything else
        are rejected.
        """
        if value is None:
            return default
        if isinstance(value, bool):
            cls._invalid(f"{name} must be an integer, not a boolean (got {value!r})")
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and value.isascii() and value.isdigit():
            number = int(value)
        else:
            cls._invalid(f"{name} must be an integer (got {value!r})")
        if not minimum <= number <= maximum:
            cls._invalid(
                f"{name} must be between {minimum:,} and {maximum:,} "
                f"(got {number:,})"
            )
        return number

    # ------------------------------------------------------------------ #
    # join mode
    # ------------------------------------------------------------------ #

    def _run_join(
        self,
        strings: list[str],
        delimiter: Any,
        style: Any,
        drop_empty: Any,
        empty_as: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Join items with a delimiter and an optional conjunction."""
        if style is None:
            style = "plain"
        if style not in self.STYLES:
            self._invalid(
                f"style must be one of: {', '.join(self.STYLES)} "
                f"(got {style!r})"
            )
        clean_drop = self._validate_flag(drop_empty, "drop_empty")
        kept = [item for item in strings if item] if clean_drop else strings
        items_dropped = len(strings) - len(kept)
        clean_delim = self._validate_separator(
            delimiter,
            "delimiter",
            default=", ",
            # An empty delimiter can still be a caller mistake, but it
            # is harmless when at most one item is joined, so it is
            # only rejected when two or more items remain.
            allow_empty=len(kept) <= 1,
        )
        context = {
            **context,
            "style": style,
            "delimiter": clean_delim,
            "drop_empty": clean_drop,
            "items_dropped": items_dropped,
        }
        if not kept:
            return self._finish(context, kept, self._empty_result(empty_as))
        return self._finish(context, kept, self._join_list(kept, style, clean_delim))

    @classmethod
    def _join_list(cls, items: list[str], style: str, delimiter: str) -> str:
        """Join non-empty item lists per the requested style."""
        if len(items) == 1:
            return items[0]
        head, last = items[:-1], items[-1]
        if style == "plain":
            return delimiter.join(items)
        if style == "oxford":
            if len(items) == 2:
                # Standard short form: two items never take a comma.
                return f"{head[0]} and {last}"
            return f"{delimiter.join(head)}{delimiter}and {last}"
        if style == "and":
            if len(items) == 2:
                return f"{head[0]} and {last}"
            # Documented without the final comma: a, b and c.
            return f"{delimiter.join(head)} and {last}"
        # style == "or"
        if len(items) == 2:
            return f"{head[0]} or {last}"
        return f"{delimiter.join(head)}{delimiter}or {last}"

    # ------------------------------------------------------------------ #
    # join_pairs / numbered / bullet modes
    # ------------------------------------------------------------------ #

    def _run_join_pairs(
        self,
        pairs: list[tuple[str, str]],
        kv_sep: Any,
        item_delim: Any,
        empty_as: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Format key/value pairs and join them into one string."""
        clean_kv = self._validate_separator(kv_sep, "kv_sep", default="=")
        clean_delim = self._validate_separator(
            item_delim, "item_delim", default=", ", allow_empty=len(pairs) <= 1
        )
        context = {**context, "kv_sep": clean_kv, "item_delim": clean_delim}
        if not pairs:
            return self._finish(context, [], self._empty_result(empty_as))
        formatted = [f"{key}{clean_kv}{value}" for key, value in pairs]
        return self._finish(context, formatted, clean_delim.join(formatted))

    def _run_numbered(
        self,
        strings: list[str],
        number_format: Any,
        start: Any,
        empty_as: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Prefix every item with its running number."""
        if number_format is None:
            number_format = "dot"
        if number_format not in self.FORMATS:
            self._invalid(
                f"number_format must be one of: {', '.join(self.FORMATS)} "
                f"(got {number_format!r})"
            )
        clean_start = self._validate_count(
            start, "start", minimum=0, maximum=999_999, default=1
        )
        context = {
            **context,
            "number_format": number_format,
            "start": clean_start,
        }
        if not strings:
            return self._finish(context, [], self._empty_result(empty_as))
        suffix = "." if number_format == "dot" else ")"
        numbered = [
            f"{number}{suffix} {item}"
            for number, item in enumerate(strings, start=clean_start)
        ]
        return self._finish(context, numbered, "\n".join(numbered))

    def _run_bullet(
        self,
        strings: list[str],
        bullet: Any,
        empty_as: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Prefix every item with the bullet character."""
        if bullet is None:
            bullet = "-"
        if not isinstance(bullet, str):
            self._invalid(f"bullet must be a string (got {bullet!r})")
        if not bullet:
            self._invalid("bullet must be a non-empty string (got '')")
        if len(bullet) > self.max_bullet_chars:
            self._invalid(
                f"bullet exceeds the {self.max_bullet_chars}-character "
                f"limit (got {len(bullet)} characters)"
            )
        context = {**context, "bullet": bullet}
        if not strings:
            return self._finish(context, [], self._empty_result(empty_as))
        bulleted = [f"{bullet} {item}" for item in strings]
        return self._finish(context, bulleted, "\n".join(bulleted))

    # ------------------------------------------------------------------ #
    # Result assembly
    # ------------------------------------------------------------------ #

    @staticmethod
    def _empty_result(empty_as: str) -> str:
        """Return the configured result for an empty item list."""
        return "" if empty_as == "empty" else EMPTY_NOTE

    @staticmethod
    def _finish(
        context: dict[str, Any],
        output_items: list,
        result: str,
    ) -> dict[str, Any]:
        """Merge the produced string into the result payload."""
        return {
            **context,
            "output_items": len(output_items),
            "result": result,
        }
