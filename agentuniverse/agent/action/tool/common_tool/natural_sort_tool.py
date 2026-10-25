#!/usr/bin/env python3
"""Natural, human-aware ordering of string lists with embedded numbers."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import sys
import unicodedata
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_ASCII_DIGITS = frozenset("0123456789")

# Byte flag table for locating ASCII digit runs in O(n) with C-speed scans:
# digit bytes map to 0, every other byte (all UTF-8 lead/continuation bytes are
# >= 0x80, so multibyte characters can never be split) maps to 1. A digit run
# then spans from one ``find(0, ...)`` to the following ``find(1, ...)``.
_DIGIT_FLAG = bytes(0 if 0x30 <= byte <= 0x39 else 1 for byte in range(256))


def _int_str_limit() -> float:
    """Python's int<->str conversion digit limit (inf before Python 3.11).

    Digit runs longer than this must never be routed through ``int()`` /
    ``str()``: on Python 3.11+ both directions raise ValueError past the
    limit, so numeric keys are built from the digit strings directly.
    """
    getter = getattr(sys, "get_int_max_str_digits", None)
    return float(getter()) if getter is not None else float("inf")

# Chunk kinds produced by the tokenizer.
_TEXT = "text"
_NUM = "num"
_DEC = "dec"


class NaturalSortTool(Tool):
    """Natural (human-aware) ordering for lists of strings.

    Chunking rules
    --------------
    * A maximal run of ASCII digits (0-9) is one number chunk compared by its
      integer value, so ``file2`` sorts before ``file10``. Values of long runs
      (1,000+ digits, including runs beyond Python's 4,300-digit int<->str
      conversion limit) are compared as exact arbitrary-precision digit
      strings, never floats and never through ``int()``.
    * Every maximal run of non-digit characters is one text chunk compared
      code point by code point after Unicode NFD normalization (no locale is
      consulted, ever), so precomposed and decomposed accents are equal keys
      (``café`` == ``cafe\\u0301``) and an accented letter sorts beside its
      base letter instead of after every ASCII letter.
    * A number chunk sorts before a text chunk at the same position, matching
      the common human expectation that ``1a`` comes before ``a1``.
    * Embedded signs are NOT part of numbers: in ``a-1`` the ``-`` is
      punctuation, so the chunks are ``a`` / ``-`` / ``1``. Only bare digit
      runs (and decimal groups when ``decimal=True``) are numeric.
    * Whitespace is ordinary text: it compares by code point after the
      optional case folding, so ``a\\tb`` < ``a\\nb`` < ``a b`` < ``ab``.
    * When two chunk lists are equal up to the length of the shorter one, the
      shorter list sorts first (``file2`` < ``file2b``), and the empty string
      (zero chunks) sorts before every non-empty string.

    Case folding
    ------------
    With ``case_sensitive=False`` (the default) text chunks are compared via
    ``str.casefold()`` applied after NFD normalization (full Unicode case
    folding, e.g. ``ss`` and ``ß`` compare equal). Strings whose folded chunk
    keys are equal keep their input order because Python's sort is stable.

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
    run merge into one decimal chunk compared as an exact decimal value,
    so ``['1.5', '1.10']`` sorts as ``['1.10', '1.5']`` because 1.10 == 1.1
    numerically (without ``decimal`` the chunk-wise result ``1.5 < 1.10`` is
    the classic lexicographic gotcha). Merging is greedy left-to-right:
    ``1.2.3`` becomes ``1.2`` / ``.`` / ``3``. A decimal chunk requires
    digits on both sides of the dot; ``.5`` and ``5.`` stay text plus number.
    The comparison is exact string arithmetic (integer part by length then
    digits, fraction part digit-wise), so decimal groups of any length work
    without float or Decimal conversion.

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

    compare mode
    ------------
    ``first_difference`` is the index of the first differing chunk computed
    over the WHOLE chunk lists, never over the capped ``chunks`` explanation
    list (when the difference lies beyond ``max_compare_chunks`` the index is
    still reported and ``chunks_truncated`` is set). ``prefix_relation`` is
    reported whenever one side's chunk list is a strict prefix of the other's,
    including the empty string against anything.

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

    def _chunks(self, text: str, options: dict[str, Any]) -> list[tuple[str, Any, Any, Any, int]]:
        """Split one string into (kind, raw, key_value, display, tiebreak) tuples."""
        fold = not options["case_sensitive"]
        unicode_mode = options["unicode_digits"]
        if unicode_mode == "reject" and not text.isascii():
            # ASCII text cannot contain non-ASCII decimal digits: scan only
            # when non-ASCII characters are present.
            for position, char in enumerate(text):
                if char not in _ASCII_DIGITS and char.isdecimal():
                    raise ValueError(
                        f"non-ASCII decimal digit {char!r} at index {position}; "
                        "use unicode_digits='text' or 'normalize'"
                    )
        tokens = self._tokens(text, unicode_mode)
        if options["decimal"]:
            tokens = self._merge_decimals(tokens)
        if options["number_mode"] == "whole" and not self._is_whole_number(tokens):
            return [(_TEXT, text, self._text_key(text, fold), None, 0)]
        chunks: list[tuple[str, Any, Any, Any, int]] = []
        fewer_first = options["leading_zeros"] == "fewer_first"
        for kind, raw, ascii_digits in tokens:
            if kind == _TEXT:
                chunks.append((_TEXT, raw, self._text_key(raw, fold), None, 0))
            elif kind == _NUM:
                # Numeric key without int(): (digit count, digit string) of the
                # zero-stripped digits orders exactly like the integer value
                # with arbitrary precision and no int<->str length limit.
                stripped = ascii_digits.lstrip("0")
                key_value = ((len(stripped), stripped), "")
                chunks.append((_NUM, raw, key_value, self._num_display(ascii_digits, stripped), len(raw) if fewer_first else 0))
            else:
                # Decimal group "int.frac": exact string arithmetic. The
                # integer part keys like a number chunk; the fraction strips
                # trailing zeros so 1.10 == 1.1, and digit-wise comparison of
                # the remainder is exactly numeric fraction comparison.
                int_part, _, frac_part = ascii_digits.partition(".")
                int_stripped = int_part.lstrip("0")
                key_value = ((len(int_stripped), int_stripped), frac_part.rstrip("0"))
                # tie-break on the total raw digit count (the dot is not a digit)
                tiebreak = (len(raw) - 1) if fewer_first else 0
                chunks.append((_DEC, raw, key_value, f"{int_stripped or '0'}.{frac_part}", tiebreak))
        return chunks

    @staticmethod
    def _text_key(raw: str, fold: bool) -> str:
        """NFD-normalized text key, optionally casefolded (NFD first)."""
        text = raw if raw.isascii() else unicodedata.normalize("NFD", raw)
        return text.casefold() if fold else text

    @staticmethod
    def _num_display(digits: str, stripped: str) -> Any:
        """Display an int for safe sizes, else the canonical digit string."""
        if len(digits) <= _int_str_limit():
            return int(digits)
        # Beyond Python's int<->str conversion limit an int could not even be
        # serialized back; report the exact zero-stripped digit string.
        return stripped or "0"

    def _tokens(self, text: str, unicode_mode: str) -> list[tuple[str, str, str]]:
        """Tokenize into (kind, raw, ascii_digits) where kind is text/num."""
        if unicode_mode != "normalize" or text.isascii():
            # ASCII text (and any text in non-normalize modes) has no
            # non-ASCII decimal digits: no unicode-aware scan is needed.
            return self._ascii_tokens(text)

        # Unicode-aware scan: Nd characters (including ASCII digits) join the
        # current number run, everything else joins the current text run.
        # str.isdecimal() is exactly Unicode category Nd.
        runs: list[list[str]] = []
        kinds: list[str] = []
        for char in text:
            is_digit = char in _ASCII_DIGITS or char.isdecimal()
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
    def _ascii_tokens(text: str) -> list[tuple[str, str, str]]:
        """Tokenize with ASCII digit runs only, via O(n) C byte scans.

        ASCII digit runs are located by flagging the ten digit bytes in the
        UTF-8 encoding (multibyte characters can never be flagged: every UTF-8
        lead/continuation byte is >= 0x80) and using two ``bytes.find`` calls
        per run. A regex instead re-attempts its pattern at every position of
        the string, which is pathological on very long items (a 20k-char item
        is scanned up to 20k times). Lone surrogates round-trip through
        ``surrogatepass`` so every input string is encodable.
        """
        encoded = text.encode("utf-8", "surrogatepass")
        flagged = encoded.translate(_DIGIT_FLAG)
        tokens: list[tuple[str, str, str]] = []
        position = 0
        size = len(encoded)
        while True:
            start = flagged.find(0, position)
            if start < 0:
                break
            end = flagged.find(1, start)
            if end < 0:
                end = size
            if start > position:
                tokens.append((_TEXT, encoded[position:start].decode("utf-8", "surrogatepass"), ""))
            digit_run = encoded[start:end].decode("ascii")
            tokens.append((_NUM, digit_run, digit_run))
            position = end
        if position < size:
            tokens.append((_TEXT, encoded[position:].decode("utf-8", "surrogatepass"), ""))
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
    def _key(chunks: list[tuple[str, Any, Any, Any, int]]) -> tuple:
        """Comparable key: number chunks (0, value, tiebreak), text chunks (1, folded)."""
        return tuple(
            (1, chunk[2]) if chunk[0] == _TEXT else (0, chunk[2], chunk[4])
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

    def _chunk_repr(self, chunk: tuple[str, Any, Any, Any, int], truncate: bool = True) -> Any:
        kind, raw, _, value, _ = chunk
        shown = raw
        if truncate and len(shown) > self.preview_chunk_length:
            shown = shown[: self.preview_chunk_length] + "..."
        if kind == _TEXT:
            return shown
        if kind == _NUM:
            return {"number": shown, "value": value}
        return {"decimal": shown, "value": value}

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
        # first_difference is computed over the WHOLE shared chunk range, not
        # over the (possibly capped) explanation list, so a difference beyond
        # max_compare_chunks is still reported honestly.
        first_difference = next(
            (index for index in range(shared) if key_a[index] != key_b[index]),
            None,
        )
        if key_a == key_b:
            result = 0
        else:
            result = -1 if key_a < key_b else 1
            if first_difference is None and len(chunks_a) != len(chunks_b):
                # Every shared chunk is equal (including the vacuous case of
                # zero shared chunks: the empty string is a prefix of any
                # non-empty string).
                prefix_relation = "a_is_prefix" if len(chunks_a) < len(chunks_b) else "b_is_prefix"
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
