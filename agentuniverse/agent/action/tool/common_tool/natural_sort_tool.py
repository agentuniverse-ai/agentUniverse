#!/usr/bin/env python3
"""Natural, human-aware ordering of string lists with embedded numbers."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
import unicodedata
from decimal import Decimal
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_ASCII_NUM_RUN = re.compile(r"[0-9]+")
_ASCII_DIGITS = frozenset("0123456789")

# Chunk kinds produced by the tokenizer.
_TEXT = "text"
_NUM = "num"
_DEC = "dec"


class NaturalSortTool(Tool):
    """Natural (human-aware) ordering for lists of strings.

    Chunking rules
    --------------
    * A maximal run of ASCII digits (0-9) is one number chunk compared by its
      integer value, so ``file2`` sorts before ``file10``. Values of runs of
      1,000+ digits are compared as Python ints (arbitrary precision, never
      floats).
    * Every maximal run of non-digit characters is one text chunk compared
      code point by code point (no locale is consulted, ever).
    * A number chunk sorts before a text chunk at the same position, matching
      the common human expectation that ``1a`` comes before ``a1``.
    * Embedded signs are NOT part of numbers: in ``a-1`` the ``-`` is
      punctuation, so the chunks are ``a`` / ``-`` / ``1``. Only bare digit
      runs (and decimal groups when ``decimal=True``) are numeric.
    * Whitespace is ordinary text: it compares by code point after the
      optional case folding, so ``a\\tb`` < ``a\\nb`` < ``a b`` < ``ab``.
    * When two chunk lists are equal up to the length of the shorter one, the
      shorter list sorts first (``file2`` < ``file2b``).

    Case folding
    ------------
    With ``case_sensitive=False`` (the default) text chunks are compared via
    ``str.casefold()`` (full Unicode case folding, e.g. ``ss`` and ``ß``
    compare equal). Strings whose folded chunk keys are equal keep their
    input order because Python's sort is stable.

    Leading zeros
    -------------
    ``leading_zeros="stable"`` (the default): ``002`` and ``2`` compare as
    EQUAL keys (numeric value only), so equal-key items keep their input
    order. This matches the natsort reference oracle. With
    ``leading_zeros="fewer_first"`` numerically equal numbers break the tie
    by fewer leading zeros first: ``2`` < ``02`` < ``002`` (decimal groups
    tie-break by their total raw digit count: ``1.1`` < ``1.10``).

    Decimal groups
    --------------
    With ``decimal=True`` a digit run, a single ``.``, and a following digit
    run merge into one decimal chunk compared as an exact ``Decimal`` value,
    so ``['1.5', '1.10']`` sorts as ``['1.10', '1.5']`` because 1.10 == 1.1
    numerically (without ``decimal`` the chunk-wise result ``1.5 < 1.10`` is
    the classic lexicographic gotcha). Merging is greedy left-to-right:
    ``1.2.3`` becomes ``1.2`` / ``.`` / ``3``. A decimal chunk requires
    digits on both sides of the dot; ``.5`` and ``5.`` stay text plus number.

    Unicode digits
    --------------
    Non-ASCII decimal digits (Unicode category Nd, e.g. ``٣``) are NOT
    numbers by default. ``unicode_digits="text"`` (default) treats them as
    plain text, ``"normalize"`` folds each Nd character into its numeric
    value via ``unicodedata.digit`` so such runs join ASCII runs as one
    number, and ``"reject"`` refuses inputs containing them. Superscripts
    such as ``²`` (category No) are never numbers.

    Number modes
    ------------
    ``number_mode="chunked"`` (default) turns every embedded digit run into
    a numeric chunk. ``number_mode="whole"`` recognizes a number only when
    the ENTIRE string is one number (or one decimal group with
    ``decimal=True``); strings with embedded digits then compare as plain
    text, which keeps identifiers such as ``A-002`` lexicographically
    together while pure numbers still compare numerically.

    Determinism
    -----------
    The output depends only on the input and the selected options: no locale
    calls, no time, no randomness, no floats. The same input always yields a
    byte-identical result, and the input list is never mutated.
    """

    max_items: int = 10_000
    max_item_length: int = 10_000
    max_key_preview_items: int = 100
    max_violations: int = 100
    max_compare_chunks: int = 200
    preview_chunk_length: int = 200

    _MODES: ClassVar[frozenset[str]] = frozenset({"sort", "rank", "compare", "is_sorted"})
    _NUMBER_MODES: ClassVar[frozenset[str]] = frozenset({"chunked", "whole"})
    _UNICODE_DIGITS_MODES: ClassVar[frozenset[str]] = frozenset({"text", "normalize", "reject"})
    _LEADING_ZEROS_MODES: ClassVar[frozenset[str]] = frozenset({"stable", "fewer_first"})

    def execute(
        self,
        mode: str,
        items: list[str] | None = None,
        value: str | None = None,
        reference: list[str] | None = None,
        a: str | None = None,
        b: str | None = None,
        case_sensitive: bool = False,
        number_mode: str = "chunked",
        decimal: bool = False,
        unicode_digits: str = "text",
        leading_zeros: str = "stable",
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._choice(mode, "mode", self._MODES)
            options = {
                "case_sensitive": self._flag(case_sensitive, "case_sensitive"),
                "number_mode": self._choice(number_mode, "number_mode", self._NUMBER_MODES),
                "decimal": self._flag(decimal, "decimal"),
                "unicode_digits": self._choice(unicode_digits, "unicode_digits", self._UNICODE_DIGITS_MODES),
                "leading_zeros": self._choice(leading_zeros, "leading_zeros", self._LEADING_ZEROS_MODES),
            }
            if operation == "sort":
                return self._sort(self._items(items, "items"), options)
            if operation == "is_sorted":
                return self._is_sorted(self._items(items, "items"), options)
            if operation == "rank":
                return self._rank(self._string(value, "value"), self._items(reference, "reference"), options)
            return self._compare(self._string(a, "a"), self._string(b, "b"), options)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Natural sort failed: {exc}")

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_config(self) -> None:
        for name in ("max_items", "max_item_length", "max_key_preview_items", "max_violations", "max_compare_chunks"):
            bound = getattr(self, name)
            if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if isinstance(self.preview_chunk_length, bool) or not isinstance(self.preview_chunk_length, int) or self.preview_chunk_length <= 0:
            raise ValueError("preview_chunk_length must be a positive integer")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    @staticmethod
    def _choice(raw: Any, name: str, allowed: frozenset[str]) -> str:
        if not isinstance(raw, str):
            raise TypeError(f"{name} must be a string")
        value = raw.strip().lower()
        if value not in allowed:
            raise ValueError(f"{name} must be one of {sorted(allowed)}")
        return value

    @staticmethod
    def _flag(raw: Any, name: str) -> bool:
        if not isinstance(raw, bool):
            raise TypeError(f"{name} must be a boolean")
        return raw

    def _items(self, raw: Any, name: str) -> list[str]:
        if not isinstance(raw, list):
            raise TypeError(f"{name} must be a list of strings")
        if len(raw) > self.max_items:
            raise ValueError(f"{name} exceeds max_items ({self.max_items})")
        for index, item in enumerate(raw):
            if isinstance(item, bool) or not isinstance(item, str):
                raise TypeError(f"{name}[{index}] must be a string")
            if len(item) > self.max_item_length:
                raise ValueError(f"{name}[{index}] exceeds max_item_length ({self.max_item_length})")
        return raw

    def _string(self, raw: Any, name: str) -> str:
        if not isinstance(raw, str):
            raise TypeError(f"{name} must be a string")
        if len(raw) > self.max_item_length:
            raise ValueError(f"{name} exceeds max_item_length ({self.max_item_length})")
        return raw

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def _chunks(self, text: str, options: dict[str, Any]) -> list[tuple[str, Any, Any, int]]:
        """Split one string into (kind, raw, value, tiebreak) chunk tuples."""
        fold = not options["case_sensitive"]
        unicode_mode = options["unicode_digits"]
        if unicode_mode == "reject":
            for position, char in enumerate(text):
                if char not in _ASCII_DIGITS and unicodedata.category(char) == "Nd":
                    raise ValueError(
                        f"non-ASCII decimal digit {char!r} at index {position}; "
                        "use unicode_digits='text' or 'normalize'"
                    )
        tokens = self._tokens(text, unicode_mode)
        if options["decimal"]:
            tokens = self._merge_decimals(tokens)
        if options["number_mode"] == "whole" and not self._is_whole_number(tokens):
            return [(_TEXT, text, text.casefold() if fold else text, 0)]
        chunks: list[tuple[str, Any, Any, int]] = []
        fewer_first = options["leading_zeros"] == "fewer_first"
        for kind, raw, ascii_digits in tokens:
            if kind == _TEXT:
                chunks.append((_TEXT, raw, raw.casefold() if fold else raw, 0))
            elif kind == _NUM:
                chunks.append((_NUM, raw, int(ascii_digits), len(raw) if fewer_first else 0))
            else:
                # Decimal group "int.frac": exact Decimal value, tie-break on
                # the total raw digit count (the dot itself is not a digit).
                tiebreak = (len(raw) - 1) if fewer_first else 0
                chunks.append((_DEC, raw, Decimal(ascii_digits), tiebreak))
        return chunks

    def _tokens(self, text: str, unicode_mode: str) -> list[tuple[str, str, str]]:
        """Tokenize into (kind, raw, ascii_digits) where kind is text/num."""
        if unicode_mode != "normalize":
            tokens: list[tuple[str, str, str]] = []
            position = 0
            for match in _ASCII_NUM_RUN.finditer(text):
                if match.start() > position:
                    tokens.append((_TEXT, text[position:match.start()], ""))
                tokens.append((_NUM, match.group(0), match.group(0)))
                position = match.end()
            if position < len(text):
                tokens.append((_TEXT, text[position:], ""))
            return tokens

        # Unicode-aware scan: Nd characters (including ASCII digits) join the
        # current number run, everything else joins the current text run.
        runs: list[list[str]] = []
        kinds: list[str] = []
        for char in text:
            is_digit = char in _ASCII_DIGITS or unicodedata.category(char) == "Nd"
            wanted = _NUM if is_digit else _TEXT
            if kinds and kinds[-1] == wanted:
                runs[-1].append(char)
            else:
                runs.append([char])
                kinds.append(wanted)
        tokens = []
        for kind, chars in zip(kinds, runs):
            raw = "".join(chars)
            if kind == _NUM:
                ascii_digits = "".join(
                    char if char in _ASCII_DIGITS else str(unicodedata.digit(char)) for char in raw
                )
                tokens.append((_NUM, raw, ascii_digits))
            else:
                tokens.append((_TEXT, raw, ""))
        return tokens

    @staticmethod
    def _merge_decimals(tokens: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
        """Greedy left-to-right merge of num, '.', num token triples."""
        merged: list[tuple[str, str, str]] = []
        index = 0
        while index < len(tokens):
            if (
                index + 2 < len(tokens)
                and tokens[index][0] == _NUM
                and tokens[index + 1][0] == _TEXT
                and tokens[index + 1][1] == "."
                and tokens[index + 2][0] == _NUM
            ):
                int_part, frac_part = tokens[index][2], tokens[index + 2][2]
                raw = f"{tokens[index][1]}.{tokens[index + 2][1]}"
                merged.append((_DEC, raw, f"{int_part}.{frac_part}"))
                index += 3
            else:
                merged.append(tokens[index])
                index += 1
        return merged

    @staticmethod
    def _is_whole_number(tokens: list[tuple[str, str, str]]) -> bool:
        return len(tokens) == 1 and tokens[0][0] in (_NUM, _DEC)

    @staticmethod
    def _key(chunks: list[tuple[str, Any, Any, int]]) -> tuple:
        """Comparable key: number chunks (0, value, tiebreak), text chunks (1, folded)."""
        return tuple(
            (1, chunk[2]) if chunk[0] == _TEXT else (0, chunk[2], chunk[3])
            for chunk in chunks
        )

    def _sort_key(self, text: str, options: dict[str, Any]):
        return self._key(self._chunks(text, options))

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------

    def _sort(self, items: list[str], options: dict[str, Any]) -> dict[str, Any]:
        keys = [self._sort_key(item, options) for item in items]
        order = sorted(range(len(items)), key=lambda index: keys[index])
        sorted_items = [items[index] for index in order]
        preview, truncated = self._key_preview(items, keys, options)
        return {
            "status": "success",
            "mode": "sort",
            "sorted": sorted_items,
            "count": len(items),
            "swap_count": _inversion_count(keys),
            "key_preview": preview,
            "key_preview_truncated": truncated,
            "options": dict(options),
        }

    def _key_preview(self, items: list[str], keys: list[tuple], options: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        limit = min(len(items), self.max_key_preview_items)
        preview: dict[str, Any] = {}
        for index in range(limit):
            preview[items[index]] = [
                self._chunk_repr(chunk) for chunk in self._chunks(items[index], options)
            ]
        return preview, len(items) > limit

    def _chunk_repr(self, chunk: tuple[str, Any, Any, int], truncate: bool = True) -> Any:
        kind, raw, value, _ = chunk
        shown = raw
        if truncate and len(shown) > self.preview_chunk_length:
            shown = shown[: self.preview_chunk_length] + "..."
        if kind == _TEXT:
            return shown
        if kind == _NUM:
            return {"number": shown, "value": value}
        return {"decimal": shown, "value": str(value)}

    def _is_sorted(self, items: list[str], options: dict[str, Any]) -> dict[str, Any]:
        keys = [self._sort_key(item, options) for item in items]
        violations: list[list[str]] = []
        truncated = False
        for index in range(len(items) - 1):
            if keys[index] > keys[index + 1]:
                if len(violations) >= self.max_violations:
                    truncated = True
                    break
                violations.append([items[index], items[index + 1]])
        return {
            "status": "success",
            "mode": "is_sorted",
            "sorted": not violations,
            "count": len(items),
            "violations": violations,
            "violations_truncated": truncated,
            "options": dict(options),
        }

    def _rank(self, value: str, reference: list[str], options: dict[str, Any]) -> dict[str, Any]:
        keys = [self._sort_key(item, options) for item in reference]
        order = sorted(range(len(reference)), key=lambda index: keys[index])
        sorted_items = [reference[index] for index in order]
        sorted_keys = [keys[index] for index in order]
        target = self._sort_key(value, options)
        low, high = 0, len(sorted_keys)
        while low < high:
            middle = (low + high) // 2
            if sorted_keys[middle] < target:
                low = middle + 1
            else:
                high = middle
        return {
            "status": "success",
            "mode": "rank",
            "value": value,
            "position": low,
            "present": any(key == target for key in sorted_keys),
            "previous": sorted_items[low - 1] if low > 0 else None,
            "next": sorted_items[low] if low < len(sorted_items) else None,
            "reference_length": len(reference),
            "options": dict(options),
        }

    def _compare(self, a: str, b: str, options: dict[str, Any]) -> dict[str, Any]:
        chunks_a = self._chunks(a, options)
        chunks_b = self._chunks(b, options)
        key_a, key_b = self._key(chunks_a), self._key(chunks_b)
        pairs: list[dict[str, Any]] = []
        truncated = False
        shared = min(len(chunks_a), len(chunks_b))
        for index in range(shared):
            if len(pairs) >= self.max_compare_chunks:
                truncated = True
                break
            part_a, part_b = key_a[index], key_b[index]
            relation = "<" if part_a < part_b else (">" if part_a > part_b else "=")
            pairs.append(
                {
                    "a": self._chunk_repr(chunks_a[index]),
                    "b": self._chunk_repr(chunks_b[index]),
                    "relation": relation,
                }
            )
        prefix_relation = None
        if key_a == key_b:
            result = 0
        else:
            result = -1 if key_a < key_b else 1
            if shared and all(pair["relation"] == "=" for pair in pairs) and not truncated:
                prefix_relation = "a_is_prefix" if len(chunks_a) < len(chunks_b) else "b_is_prefix"
        first_difference = next(
            (index for index, pair in enumerate(pairs) if pair["relation"] != "="),
            None,
        )
        return {
            "status": "success",
            "mode": "compare",
            "result": result,
            "chunks": pairs,
            "chunks_truncated": truncated,
            "first_difference": first_difference,
            "prefix_relation": prefix_relation,
            "options": dict(options),
        }


def _inversion_count(keys: list) -> int:
    """Count pairs i < j with keys[i] > keys[j] via merge sort (O(n log n)).

    This is the minimal number of adjacent swaps needed to sort the list,
    which the tool reports as ``swap_count``.
    """

    def sort_count(sequence: list) -> tuple[list, int]:
        if len(sequence) <= 1:
            return sequence, 0
        middle = len(sequence) // 2
        left, count_left = sort_count(sequence[:middle])
        right, count_right = sort_count(sequence[middle:])
        merged: list = []
        count = 0
        i = j = 0
        while i < len(left) and j < len(right):
            if right[j] < left[i]:
                merged.append(right[j])
                j += 1
                count += len(left) - i
            else:
                merged.append(left[i])
                i += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, count_left + count_right + count

    return sort_count(list(keys))[1]
