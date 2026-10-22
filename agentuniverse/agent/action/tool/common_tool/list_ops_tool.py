#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: list_ops_tool.py

"""Set-style operations on JSON lists, built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency list algebra utility
agents can call when merging, comparing and cleaning structured data:
union, intersection, difference, symmetric difference, deduplication,
distinct counting and flattening.

Unlike ``set`` algebra in plain Python — whose iteration order is
arbitrary and undocumented — every operation here is **stable and
documented**: ``union`` emits first occurrences in list-a order, then
previously-unseen elements in list-b order; ``intersection`` and
``difference`` keep list-a order; ``symmetric_difference`` emits the
a-only part (a order) followed by the b-only part (b order); ``dedupe``
keeps the first occurrence of every value.

Two comparison modes are supported:

* **Scalar mode** (default) — elements are compared by value. Accepted
  scalars are strings, numbers, booleans and ``null``; a ``list`` or
  ``dict`` element is rejected with a structured error naming the list
  and the offending element index. Equality follows Python semantics,
  so ``1``, ``1.0`` and ``true`` are *the same value* and collapse to
  the first occurrence's original form (``[1.0, 1]`` dedupes to
  ``[1.0]``); the strings ``"1"`` and ``"1.0"`` stay distinct.
* **Object mode** (``key="..."``) — elements are JSON objects compared
  by the value at a key path; dotted paths such as ``meta.id`` address
  nested keys. The first element per key value wins and is preserved
  whole. A missing key (or a non-object element / non-object path step)
  raises a structured error listing the list name and element index;
  key values must themselves be hashable scalars.

Modes:

* ``union`` / ``intersection`` / ``difference`` /
  ``symmetric_difference`` — two lists (``a`` required, ``b``
  required) → ``{result, counts}`` where ``counts`` carries the raw
  input lengths (``a``, ``b``), the result length, and
  ``removed``/``kept``: every result element is carried exactly once,
  so ``removed = len(a) + len(b) - len(result)`` counts the input
  occurrences that were not carried into the result, and
  ``kept = len(result)``.
* ``dedupe`` — one list, first occurrence wins, with
  ``removed_count``, a ``removed_items`` preview capped at 20 entries
  and a ``removed_items_truncated`` flag.
* ``unique_count`` — one list → ``distinct_count`` plus per-value
  counts (``value_counts``, sorted by count descending with ties in
  first-occurrence order), optionally capped via ``top_n``.
* ``flatten`` — nested lists flattened up to ``depth`` levels
  (default: fully); non-list values, including objects, are leaves.
  A list that contains itself raises a structured cycle error.

``a`` and ``b`` accept a Python list or a JSON array string
(``'[1, 2, 3]'``); each list is capped at 10,000 elements, as is the
flattened result. Empty lists are valid everywhere (``union`` with an
empty ``a`` simply returns ``b`` deduplicated).

Everything is deterministic — no randomness, no time dependence, no
network. Validation is strict and happens before any work: malformed
parameters (unknown mode, wrong types, missing ``b`` for two-list
modes, mode-specific options used with the wrong mode, non-object
elements in object mode, unhashable elements, key paths with empty
segments, out-of-bounds ``top_n``/``depth``, lists over the cap) raise
a ``ValueError`` mirroring the other common tools.
"""

# Strict validation raises ValueError with a descriptive message.
# ruff: noqa: TRY003

import json
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Scalar (hashable-comparable) JSON values accepted in scalar mode and
# as object-mode key values.
_SCALAR_TYPES = (str, int, float, bool, type(None))


class ListOpsTool(Tool):
    """Set-style operations on JSON lists, built purely on the stdlib.

    Attributes:
        max_items (int): Upper bound on the number of elements per
            input list and on the flattened result; larger inputs are
            rejected before any work.
        removed_preview_cap (int): Maximum number of removed items the
            ``dedupe`` mode reports in ``removed_items``.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "list_ops_tool"
    description: str = (
        "List algebra tool — pure Python stdlib, no network required. "
        "Set-style operations on JSON lists with stable, documented "
        "ordering — union (list-a first occurrences then unseen list-b "
        "elements), intersection and difference (list-a order) and "
        "symmetric_difference (a-only then b-only) over two lists "
        "(mode='union'/'intersection'/'difference'/'symmetric_difference'), "
        "stable first-occurrence dedupe with removed-count and capped "
        "preview (mode='dedupe'), distinct counting with per-value "
        "counts and optional top_n (mode='unique_count'), and nested-"
        "list flattening to a requested depth with a cycle guard "
        "(mode='flatten'). Scalar mode compares values (strings, "
        "numbers, booleans, null; 1, 1.0 and true collapse per Python "
        "equality); object mode (key='id' or nested 'meta.id') "
        "compares objects by key value, preserving the first element "
        "per key. Inputs accept lists or JSON array strings, capped "
        "at 10,000 elements; results carry a counts dict with a, b, "
        "result, removed and kept."
    )

    MODES: ClassVar[tuple] = (
        "union",
        "intersection",
        "difference",
        "symmetric_difference",
        "dedupe",
        "unique_count",
        "flatten",
    )
    SET_MODES: ClassVar[tuple] = (
        "union",
        "intersection",
        "difference",
        "symmetric_difference",
    )

    max_items: int = 10_000
    removed_preview_cap: int = 20

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        a: Any = None,
        b: Any = None,
        key: Any = None,
        top_n: Any = None,
        depth: Any = None,
    ) -> dict[str, Any]:
        """Run one list operation.

        Args:
            mode (str): One of ``union`` / ``intersection`` /
                ``difference`` / ``symmetric_difference`` / ``dedupe``
                / ``unique_count`` / ``flatten``.
            a (list | str): The primary list — a Python list or a JSON
                array string. Required for every mode; may be empty.
            b (list | str): The second list for the four set modes;
                required there and rejected everywhere else.
            key (str): Object mode — compare elements by the value at
                this key path (dotted paths like ``meta.id`` address
                nested keys). Valid for the set modes, ``dedupe`` and
                ``unique_count``; rejected for ``flatten``.
            top_n (int): ``unique_count`` only — cap the per-value
                counts list at this many entries (1-10000).
            depth (int): ``flatten`` only — flatten up to this many
                nesting levels (0-100); omit to flatten completely.

        Returns:
            Dict[str, Any]: Always ``mode``, the comparison mode
            (``by``: ``value`` or ``key``) and ``result``. The set
            modes add ``counts`` {a, b, result, removed, kept};
            ``dedupe`` adds ``removed_count``, the capped
            ``removed_items`` preview and ``removed_items_truncated``;
            ``unique_count`` adds ``distinct_count``, ``value_counts``,
            ``counts_total``, ``counts_truncated`` and ``top_n``;
            ``flatten`` adds ``depth`` and a two-entry ``counts``.

        Raises:
            ValueError: If any parameter is malformed (before any
                processing happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        self._validate_option_modes(
            mode, b=b, key=key, top_n=top_n, depth=depth
        )
        if mode == "flatten":
            return self._run_flatten(a, depth)
        if mode == "unique_count":
            return self._run_unique_count(a, key, top_n)
        if mode == "dedupe":
            return self._run_dedupe(a, key)
        return self._run_set_mode(mode, a, b, key)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any processing)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"list_ops_tool: {message}")

    # Options that only some modes understand, mapped to the modes
    # that accept them; every other mode must omit them (None).
    _OPTION_MODES: ClassVar[dict] = {
        "b": SET_MODES,
        "key": SET_MODES + ("dedupe", "unique_count"),
        "top_n": ("unique_count",),
        "depth": ("flatten",),
    }

    @classmethod
    def _validate_option_modes(cls, mode: str, **options: Any) -> None:
        """Reject mode-specific options passed with the wrong mode.

        Silently ignoring ``top_n`` in the ``union`` mode (or a
        mistyped ``depth=1`` there) would hide caller mistakes, so an
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

    def _validate_list(self, value: Any, name: str, required: bool) -> list:
        """Validate a list parameter (Python list or JSON array string).

        Empty lists are valid: set algebra over an empty list is
        well-defined (``union`` with an empty ``a`` returns ``b``
        deduplicated, ``intersection`` is empty, and so on).
        """
        if value is None:
            if required:
                self._invalid(f"{name} is required for this mode (got None)")
            self._invalid(f"{name} must be a list or JSON array (got None)")
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                self._invalid(
                    f"{name} is not valid JSON for a list (got {value!r})"
                )
            if not isinstance(parsed, list):
                self._invalid(
                    f"{name} must be a JSON array string, not "
                    f"{type(parsed).__name__} (got {value!r})"
                )
            value = parsed
        if isinstance(value, bool) or not isinstance(value, list):
            self._invalid(
                f"{name} must be a list or a JSON array string "
                f"(got {value!r})"
            )
        if len(value) > self.max_items:
            self._invalid(
                f"{name} exceeds the {self.max_items:,}-element limit "
                f"(got {len(value):,} elements)"
            )
        return value

    @classmethod
    def _validate_key(cls, key: Any) -> tuple:
        """Validate the object-mode key path and split it into parts.

        Dots are path separators, so ``meta.id`` reads
        ``a[0]["meta"]["id"]``; every segment must be non-empty
        (``a..b``, ``.a`` and ``a.`` are rejected).
        """
        if not isinstance(key, str) or not key:
            cls._invalid(f"key must be a non-empty string (got {key!r})")
        parts = key.split(".")
        if any(not part for part in parts):
            cls._invalid(
                f"key path segments must be non-empty (got {key!r})"
            )
        return tuple(parts)

    @classmethod
    def _validate_count(
        cls, value: Any, name: str, minimum: int, maximum: int
    ) -> int:
        """Validate an integer option.

        Accepts real integers and pure ASCII digit strings (so callers
        may pass ``depth="2"``); booleans, floats and anything else are
        rejected.
        """
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
    # Scalar-mode helpers (values compared by equality/hash)
    # ------------------------------------------------------------------ #

    @classmethod
    def _check_scalar(cls, element: Any, list_name: str, index: int) -> None:
        """Reject non-scalar elements with their list name and index.

        ``list`` and ``dict`` elements are unhashable and cannot take
        part in value comparison; the message points at the offending
        element and suggests object mode.
        """
        if not isinstance(element, _SCALAR_TYPES):
            cls._invalid(
                f"{list_name} element at index {index} is not a hashable "
                f"scalar (got {element!r}); scalar mode accepts strings, "
                "numbers, booleans and null — use key='...' to compare "
                "objects by a key, or flatten nested lists first"
            )

    def _first_per_scalar(self, items: list, list_name: str) -> list:
        """First occurrences of the values, in input order.

        Equality follows Python semantics: ``1``, ``1.0`` and ``True``
        are one value (the first occurrence's original form is kept),
        while ``"1"`` stays a distinct string.
        """
        seen: set = set()
        kept: list = []
        for index, element in enumerate(items):
            self._check_scalar(element, list_name, index)
            if element not in seen:
                seen.add(element)
                kept.append(element)
        return kept

    def _scalar_values(self, items: list, list_name: str) -> set:
        """The set of distinct scalar values (validated)."""
        values: set = set()
        for index, element in enumerate(items):
            self._check_scalar(element, list_name, index)
            values.add(element)
        return values

    # ------------------------------------------------------------------ #
    # Object-mode helpers (elements compared by a key path)
    # ------------------------------------------------------------------ #

    def _extract_key(
        self, element: Any, list_name: str, index: int, parts: tuple
    ) -> Any:
        """Extract and validate the key value of one object element."""
        if not isinstance(element, dict):
            self._invalid(
                f"{list_name} element at index {index} is not an object "
                f"(got {element!r}); object mode requires every element "
                "to be a JSON object"
            )
        key_text = ".".join(parts)
        current: Any = element
        for step in parts:
            if not isinstance(current, dict) or step not in current:
                if not isinstance(current, dict):
                    detail = f"'{step}' is not an object"
                else:
                    detail = f"'{step}' is missing"
                self._invalid(
                    f"{list_name} element at index {index} cannot resolve "
                    f"key path {key_text!r} ({detail})"
                )
            current = current[step]
        if not isinstance(current, _SCALAR_TYPES):
            self._invalid(
                f"{list_name} element at index {index} has an unhashable "
                f"value at key {key_text!r} (got {current!r}); key values "
                "must be strings, numbers, booleans or null"
            )
        return current

    def _first_per_key(
        self, items: list, list_name: str, parts: tuple
    ) -> list:
        """First ``(key_value, element)`` per key value, in input order."""
        seen: set = set()
        kept: list = []
        for index, element in enumerate(items):
            key_value = self._extract_key(element, list_name, index, parts)
            if key_value not in seen:
                seen.add(key_value)
                kept.append((key_value, element))
        return kept

    def _key_values(self, items: list, list_name: str, parts: tuple) -> set:
        """The set of distinct key values (validated)."""
        values: set = set()
        for index, element in enumerate(items):
            values.add(
                self._extract_key(element, list_name, index, parts)
            )
        return values

    # ------------------------------------------------------------------ #
    # union / intersection / difference / symmetric_difference
    # ------------------------------------------------------------------ #

    def _run_set_mode(
        self, mode: str, a: Any, b: Any, key: Any
    ) -> dict[str, Any]:
        """Run one two-list set operation with stable ordering."""
        list_a = self._validate_list(a, "a", required=True)
        list_b = self._validate_list(b, "b", required=True)
        if key is None:
            result, by = self._set_scalars(mode, list_a, list_b), "value"
        else:
            parts = self._validate_key(key)
            result, by = (
                self._set_keyed(mode, list_a, list_b, parts),
                "key",
            )
        kept = len(result)
        removed = len(list_a) + len(list_b) - kept
        return {
            "mode": mode,
            "by": by,
            "key": key,
            "result": result,
            "counts": {
                "a": len(list_a),
                "b": len(list_b),
                "result": kept,
                "removed": removed,
                "kept": kept,
            },
        }

    def _set_scalars(self, mode: str, list_a: list, list_b: list) -> list:
        """Scalar-mode set algebra with documented stable ordering."""
        a_first = self._first_per_scalar(list_a, "a")
        if mode == "union":
            a_values = set(a_first)
            return a_first + [
                element
                for element in self._first_per_scalar(list_b, "b")
                if element not in a_values
            ]
        b_values = self._scalar_values(list_b, "b")
        if mode == "intersection":
            return [v for v in a_first if v in b_values]
        if mode == "difference":
            return [v for v in a_first if v not in b_values]
        # symmetric_difference: a-only part first (a order), then the
        # b-only part (b order).
        a_values = set(a_first)
        return [v for v in a_first if v not in b_values] + [
            element
            for element in self._first_per_scalar(list_b, "b")
            if element not in a_values
        ]

    def _set_keyed(
        self, mode: str, list_a: list, list_b: list, parts: tuple
    ) -> list:
        """Object-mode set algebra keyed by the value at ``parts``."""
        a_kept = self._first_per_key(list_a, "a", parts)
        if mode == "union":
            a_values = {key_value for key_value, _ in a_kept}
            return [element for _, element in a_kept] + [
                element
                for key_value, element in self._first_per_key(list_b, "b", parts)
                if key_value not in a_values
            ]
        b_values = self._key_values(list_b, "b", parts)
        if mode == "intersection":
            return [
                element
                for key_value, element in a_kept
                if key_value in b_values
            ]
        if mode == "difference":
            return [
                element
                for key_value, element in a_kept
                if key_value not in b_values
            ]
        a_values = {key_value for key_value, _ in a_kept}
        return [
            element
            for key_value, element in a_kept
            if key_value not in b_values
        ] + [
            element
            for key_value, element in self._first_per_key(list_b, "b", parts)
            if key_value not in a_values
        ]

    # ------------------------------------------------------------------ #
    # dedupe mode
    # ------------------------------------------------------------------ #

    def _run_dedupe(self, a: Any, key: Any) -> dict[str, Any]:
        """Deduplicate one list, keeping first occurrences.

        ``removed_items`` lists the dropped occurrences — bare values
        in scalar mode, whole elements in object mode — capped at
        ``removed_preview_cap`` entries.
        """
        list_a = self._validate_list(a, "a", required=True)
        result: list = []
        removed: list = []
        if key is None:
            by = "value"
            seen: set = set()
            for index, element in enumerate(list_a):
                self._check_scalar(element, "a", index)
                if element not in seen:
                    seen.add(element)
                    result.append(element)
                else:
                    removed.append(element)
        else:
            by = "key"
            parts = self._validate_key(key)
            seen = set()
            for index, element in enumerate(list_a):
                key_value = self._extract_key(element, "a", index, parts)
                if key_value not in seen:
                    seen.add(key_value)
                    result.append(element)
                else:
                    removed.append(element)
        removed_count = len(removed)
        preview = removed[: self.removed_preview_cap]
        return {
            "mode": "dedupe",
            "by": by,
            "key": key,
            "result": result,
            "removed_count": removed_count,
            "removed_items": preview,
            "removed_items_truncated": removed_count > len(preview),
            "counts": {
                "a": len(list_a),
                "result": len(result),
                "removed": removed_count,
                "kept": len(result),
            },
        }

    # ------------------------------------------------------------------ #
    # unique_count mode
    # ------------------------------------------------------------------ #

    def _run_unique_count(
        self, a: Any, key: Any, top_n: Any
    ) -> dict[str, Any]:
        """Count distinct values (or key values) with per-value counts."""
        list_a = self._validate_list(a, "a", required=True)
        if key is None:
            by = "value"
            occurrences: list = []
            for index, element in enumerate(list_a):
                self._check_scalar(element, "a", index)
                occurrences.append(element)
        else:
            by = "key"
            parts = self._validate_key(key)
            occurrences = [
                self._extract_key(element, "a", index, parts)
                for index, element in enumerate(list_a)
            ]
        # Insertion order == first occurrence; ties in the frequency
        # ranking keep that order, so the output is deterministic.
        frequencies: dict[Any, int] = {}
        for value in occurrences:
            frequencies[value] = frequencies.get(value, 0) + 1
        ranked = sorted(
            ({"value": value, "count": count} for value, count in frequencies.items()),
            key=lambda entry: -entry["count"],
        )
        distinct = len(ranked)
        clean_top_n = None
        if top_n is not None:
            clean_top_n = self._validate_count(
                top_n, "top_n", minimum=1, maximum=self.max_items
            )
        shown = ranked if clean_top_n is None else ranked[:clean_top_n]
        return {
            "mode": "unique_count",
            "by": by,
            "key": key,
            "distinct_count": distinct,
            "value_counts": shown,
            "counts_total": distinct,
            "counts_truncated": len(shown) < distinct,
            "top_n": clean_top_n,
            "counts": {
                "a": len(list_a),
                "result": distinct,
                "removed": len(list_a) - distinct,
                "kept": distinct,
            },
        }

    # ------------------------------------------------------------------ #
    # flatten mode
    # ------------------------------------------------------------------ #

    def _run_flatten(self, a: Any, depth: Any) -> dict[str, Any]:
        """Flatten nested lists up to ``depth`` levels (default: all).

        Non-list values — including objects — are leaves. The id-based
        cycle guard tracks only the lists on the current nesting path,
        so the same list object appearing twice as a sibling is a
        legal diamond, while self-containment raises.
        """
        list_a = self._validate_list(a, "a", required=True)
        clean_depth = None
        if depth is not None:
            clean_depth = self._validate_count(
                depth, "depth", minimum=0, maximum=100
            )
        result: list = []
        self._walk_flatten(list_a, clean_depth, (id(list_a),), result)
        return {
            "mode": "flatten",
            "depth": clean_depth,
            "result": result,
            "counts": {"a": len(list_a), "result": len(result)},
        }

    def _walk_flatten(
        self,
        items: list,
        remaining: int | None,
        path_ids: tuple,
        result: list,
    ) -> None:
        """Recursively splice nested lists into ``result``."""
        for element in items:
            if isinstance(element, list):
                if id(element) in path_ids:
                    self._invalid(
                        "flatten: cycle detected — a nested list "
                        "contains itself and cannot be flattened"
                    )
                if remaining is None or remaining > 0:
                    next_remaining = (
                        None if remaining is None else remaining - 1
                    )
                    self._walk_flatten(
                        element,
                        next_remaining,
                        path_ids + (id(element),),
                        result,
                    )
                else:
                    result.append(element)
            else:
                result.append(element)
            if len(result) > self.max_items:
                self._invalid(
                    "flatten: flattened result exceeds the "
                    f"{self.max_items:,}-element limit"
                )
