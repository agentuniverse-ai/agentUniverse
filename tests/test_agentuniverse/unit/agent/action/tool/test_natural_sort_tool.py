# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for NaturalSortTool: ground truths, option behavior, and natsort parity."""

import json
import os
import random
import sys
import unittest

from agentuniverse.agent.action.tool.common_tool import natural_sort_tool as natural_module
from agentuniverse.agent.action.tool.common_tool.natural_sort_tool import NaturalSortTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

try:
    import natsort
    from natsort import ns
    NATSORT_AVAILABLE = True
except ImportError:  # pragma: no cover - oracle is an optional test dependency
    NATSORT_AVAILABLE = False

YAML_PATH = os.path.join(os.path.dirname(natural_module.__file__), "natural_sort_tool.yaml")

# Fixed seed base so the parity batteries are byte-reproducible forever.
BATTERY_SEED = 20261021
BATTERY_LISTS = 500


def _brute_inversions(values):
    """Reference O(n^2) inversion count used to validate swap_count."""
    count = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] > values[j]:
                count += 1
    return count


class NaturalSortToolTest(unittest.TestCase):
    """Unit tests for NaturalSortTool modes, options, and documented rules."""

    def setUp(self):
        self.tool = NaturalSortTool()

    def _sorted(self, items, **options):
        result = self.tool.execute(mode="sort", items=list(items), **options)
        self.assertEqual(result["status"], "success", result.get("error"))
        return result["sorted"]

    # -- classic ground truths -----------------------------------------

    def test_classic_sequences(self):
        """Verify the canonical natural-order examples humans expect."""
        self.assertEqual(self._sorted(["a1", "a2", "a10", "a20", "a100"]),
                         ["a1", "a2", "a10", "a20", "a100"])
        self.assertEqual(self._sorted(["a100", "a20", "a10", "a2", "a1"]),
                         ["a1", "a2", "a10", "a20", "a100"])
        self.assertEqual(self._sorted(["file_10", "file_9"]),
                         ["file_9", "file_10"])
        self.assertEqual(self._sorted(["file_9", "file_10", "file_1"]),
                         ["file_1", "file_9", "file_10"])

    def test_windows_explorer_mixes(self):
        """Verify Windows-Explorer-like name mixes order numerically."""
        self.assertEqual(
            self._sorted(["file (2).txt", "file (10).txt", "file (1).txt"]),
            ["file (1).txt", "file (2).txt", "file (10).txt"],
        )
        self.assertEqual(
            self._sorted(["Chapter 10.doc", "Chapter 2.doc", "chapter 1.doc"]),
            ["chapter 1.doc", "Chapter 2.doc", "Chapter 10.doc"],
        )
        self.assertEqual(
            self._sorted(["img99.png", "IMG12.png", "img100.png"]),
            ["IMG12.png", "img99.png", "img100.png"],
        )

    def test_numbers_sort_before_text(self):
        """Verify a number chunk sorts before a text chunk at the same position."""
        self.assertEqual(self._sorted(["a1", "1a", "2a", "a2"]), ["1a", "2a", "a1", "a2"])
        self.assertEqual(self._sorted(["z", "文件1", "1文件", "1"]), ["1", "1文件", "z", "文件1"])

    def test_cjk_orders_by_code_point_and_number(self):
        """Verify CJK text chunks compare by code point while numbers compare numerically."""
        self.assertEqual(self._sorted(["文件10", "文件2", "文件1"]), ["文件1", "文件2", "文件10"])
        # '报' (U+62A5) sorts before '文' (U+6587) by code point.
        self.assertEqual(self._sorted(["文件10", "报告2", "文件2"]), ["报告2", "文件2", "文件10"])

    def test_signs_are_punctuation(self):
        """Verify embedded signs are not part of numbers: a-1 chunks as a / - / 1."""
        self.assertEqual(self._sorted(["a-10", "a-2", "a-1"]), ["a-1", "a-2", "a-10"])
        self.assertEqual(self._sorted(["a1", "a-1", "a-2", "a-10"]), ["a1", "a-1", "a-2", "a-10"])

    def test_whitespace_is_text(self):
        """Verify whitespace compares by code point after folding."""
        self.assertEqual(self._sorted(["a b", "a\tb", "a\nb", "ab", "a  b"]),
                         ["a\tb", "a\nb", "a  b", "a b", "ab"])

    def test_empty_strings_sort_first(self):
        """Verify empty strings sort before everything and survive duplicates."""
        self.assertEqual(self._sorted(["a", "", "1", "", "a1"]), ["", "", "1", "a", "a1"])

    def test_prefix_rule(self):
        """Verify equal chunk prefixes order the shorter list first."""
        self.assertEqual(self._sorted(["file2b", "file2", "file10"]), ["file2", "file2b", "file10"])

    def test_thousand_digit_numbers(self):
        """Verify 1,000+ digit runs compare by arbitrary-precision integer value."""
        nines = "9" * 1200
        googol_plus = "1" + "0" * 1201
        self.assertEqual(self._sorted([googol_plus, nines, "5"]), ["5", nines, googol_plus])
        # Different digit-count runs never fall back to text comparison.
        self.assertEqual(self._sorted(["1" + "0" * 1000, "9" * 100, "8" * 99]),
                         ["8" * 99, "9" * 100, "1" + "0" * 1000])

    def test_digit_runs_beyond_int_str_limit(self):
        """Verify runs longer than Python's 4,300-digit int<->str limit still work.

        Python 3.11+ raises ValueError when int() parses (or str() renders)
        more than 4,300 digits, so the tool must never route long digit runs
        through int(): comparisons use exact digit-string keys.
        """
        limit = getattr(sys, "get_int_max_str_digits", lambda: None)()
        if limit is None:  # Python < 3.11: no limit, exercise the path anyway
            limit = 4301
        n = limit + 700
        nines, googol = "9" * n, "1" + "0" * n
        self.assertEqual(self._sorted([googol, nines, "5"]), ["5", nines, googol])
        # All four modes succeed and stay json-serializable.
        self.assertEqual(self.tool.execute(mode="is_sorted", items=[nines, "5"])["sorted"], False)
        ranked = self.tool.execute(mode="rank", value=nines, reference=["5", "3"])
        self.assertEqual((ranked["position"], ranked["previous"]), (2, "5"))
        compared = self.tool.execute(mode="compare", a=nines, b=googol)
        self.assertEqual((compared["result"], compared["first_difference"]), (-1, 0))
        result = self.tool.execute(mode="sort", items=[nines + ".1", "5"], decimal=True)
        self.assertEqual(result["sorted"], ["5", nines + ".1"])
        # The huge value is reported as its canonical digit string (an int
        # this large could not be serialized back with str()).
        preview = self.tool.execute(mode="sort", items=[nines])["key_preview"][nines]
        self.assertEqual(preview[0]["value"], nines)
        json.dumps(self.tool.execute(mode="sort", items=[nines]))

    # -- case folding ---------------------------------------------------

    def test_case_insensitive_default_uses_casefold(self):
        """Verify default case folding treats case variants as equal keys."""
        self.assertEqual(self._sorted(["b", "A", "a", "B"]), ["A", "a", "b", "B"])
        folded = self._sorted(["Weiß", "Weiss"])
        self.assertEqual(folded, ["Weiß", "Weiss"])  # casefold-equal -> stable input order

    def test_case_sensitive_mode(self):
        """Verify case_sensitive=True keeps raw code-point text comparison."""
        self.assertEqual(self._sorted(["a", "A", "b", "B"], case_sensitive=True), ["A", "B", "a", "b"])

    # -- leading zeros ---------------------------------------------------

    def test_leading_zeros_stable_default(self):
        """Verify default leading-zero policy: equal keys keep input order (natsort parity)."""
        self.assertEqual(self._sorted(["a002", "a2", "a02", "a2"]),
                         ["a002", "a2", "a02", "a2"])

    def test_leading_zeros_fewer_first(self):
        """Verify fewer_first tiebreak orders numerically equal runs by digit count."""
        self.assertEqual(self._sorted(["a002", "a2", "a02"], leading_zeros="fewer_first"),
                         ["a2", "a02", "a002"])
        self.assertEqual(self._sorted(["1.10", "1.1", "2"], decimal=True, leading_zeros="fewer_first"),
                         ["1.1", "1.10", "2"])

    # -- decimal mode ----------------------------------------------------

    def test_decimal_mode_compares_numeric_values(self):
        """Verify decimal=True compares 1.10 == 1.1 numerically, fixing the chunk gotcha."""
        self.assertEqual(self._sorted(["1.5", "1.10"]), ["1.5", "1.10"])  # chunk-wise: 5 < 10
        self.assertEqual(self._sorted(["1.5", "1.10"], decimal=True), ["1.10", "1.5"])
        self.assertEqual(self._sorted(["10.2", "1.5.1", "1.10", "1.5"], decimal=True),
                         ["1.10", "1.5", "1.5.1", "10.2"])  # greedy: 1.2.3 -> 1.2 / . / 3
        # Digits are required on both sides of the dot: '5.' and '.5' keep a
        # number/text boundary, and numbers sort before the bare '.' chunk.
        self.assertEqual(self._sorted(["5.", ".5", "5.x", "4.9"], decimal=True),
                         ["4.9", "5.", "5.x", ".5"])

    # -- number modes ----------------------------------------------------

    def test_whole_number_mode(self):
        """Verify whole mode only recognizes whole-string numbers."""
        self.assertEqual(self._sorted(["10", "9", "2"]), ["2", "9", "10"])
        self.assertEqual(self._sorted(["10", "9", "a2", "a10"], number_mode="whole"),
                         ["9", "10", "a10", "a2"])
        self.assertEqual(self._sorted(["1.5", "10", "2"], number_mode="whole", decimal=True),
                         ["1.5", "2", "10"])

    # -- unicode digits ----------------------------------------------------

    def test_unicode_digits_default_is_text(self):
        """Verify non-ASCII digits are plain text by default (documented divergence)."""
        self.assertEqual(self._sorted(["a3", "a1", "a٣"]), ["a1", "a3", "a٣"])

    def test_unicode_digits_normalize(self):
        """Verify normalize folds Nd digits to their numeric values."""
        self.assertEqual(self._sorted(["a٣", "a4", "a10"], unicode_digits="normalize"),
                         ["a٣", "a4", "a10"])
        self.assertEqual(self._sorted(["a4", "a٣", "a10"], unicode_digits="normalize"),
                         ["a٣", "a4", "a10"])
        # Mixed ASCII + Nd runs form a single number.
        self.assertEqual(self._sorted(["a١٢", "a13", "a11"], unicode_digits="normalize"),
                         ["a11", "a١٢", "a13"])
        # Superscripts (category No) are never numbers.
        self.assertEqual(self._sorted(["a²", "a1"], unicode_digits="normalize"), ["a1", "a²"])

    def test_unicode_digits_reject(self):
        """Verify reject refuses inputs containing non-ASCII decimal digits."""
        result = self.tool.execute(mode="sort", items=["a٣"], unicode_digits="reject")
        self.assertEqual(result["status"], "error")
        self.assertIn("non-ASCII decimal digit", result["error"])

    # -- stability, immutability, determinism ----------------------------

    def test_equal_keys_preserve_input_order(self):
        """Verify Python sort stability: equal keys keep input order."""
        self.assertEqual(self._sorted(["a02", "A2", "a2", "A02"]),
                         ["a02", "A2", "a2", "A02"])

    def test_input_list_is_never_mutated(self):
        """Verify the input list is untouched after sorting."""
        items = ["b10", "a2", "a02", "", "B1"]
        snapshot = list(items)
        self.tool.execute(mode="sort", items=items)
        self.assertEqual(items, snapshot)

    def test_output_is_deterministic_and_byte_identical(self):
        """Verify repeated runs produce byte-identical JSON with no hidden state."""
        items = ["file10", "file2", "File3", "z1", "Z02", "", "文件2", "文件10"]
        first = self.tool.execute(mode="sort", items=items)
        second = NaturalSortTool().execute(mode="sort", items=items)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_swap_count_matches_bruteforce_inversions(self):
        """Verify swap_count equals the minimal adjacent-swap (inversion) count."""
        for items in (["a3", "a1", "a2"], ["b2", "a10", "b1", "a2", "a1"], ["z", "y", "x", "w"]):
            result = self.tool.execute(mode="sort", items=items)
            keys = [self.tool._sort_key(item, result["options"]) for item in items]
            self.assertEqual(result["swap_count"], _brute_inversions(keys))

    # -- key preview -------------------------------------------------------

    def test_key_preview_chunk_decomposition(self):
        """Verify key_preview exposes the chunk decomposition per original string."""
        result = self.tool.execute(mode="sort", items=["file02.txt"])
        self.assertEqual(result["key_preview"]["file02.txt"], ["file", {"number": "02", "value": 2}, ".txt"])
        result = self.tool.execute(mode="sort", items=["1.10"], decimal=True)
        self.assertEqual(result["key_preview"]["1.10"], [{"decimal": "1.10", "value": "1.10"}])

    def test_key_preview_caps_and_flags(self):
        """Verify key_preview caps at max_key_preview_items and flags truncation."""
        tool = NaturalSortTool(max_key_preview_items=2)
        result = tool.execute(mode="sort", items=["a3", "a1", "a2"])
        self.assertEqual(len(result["key_preview"]), 2)
        self.assertTrue(result["key_preview_truncated"])

    # -- rank mode ---------------------------------------------------------

    def test_rank_position_and_neighbors(self):
        """Verify rank reports position plus neighboring entries."""
        result = self.tool.execute(mode="rank", value="file5", reference=["file10", "file1", "file3"])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["position"], 2)
        self.assertFalse(result["present"])
        self.assertEqual(result["previous"], "file3")
        self.assertEqual(result["next"], "file10")

    def test_rank_boundaries_and_presence(self):
        """Verify rank at both ends and exact presence."""
        reference = ["file1", "file3", "file10"]
        first = self.tool.execute(mode="rank", value="file0", reference=reference)
        self.assertEqual((first["position"], first["previous"], first["next"]), (0, None, "file1"))
        last = self.tool.execute(mode="rank", value="file99", reference=reference)
        self.assertEqual((last["position"], last["previous"], last["next"]), (3, "file10", None))
        present = self.tool.execute(mode="rank", value="file3", reference=reference)
        self.assertTrue(present["present"])
        self.assertEqual(present["position"], 1)

    # -- compare mode --------------------------------------------------------

    def test_compare_chunk_explanation(self):
        """Verify compare returns -1/0/1 with chunk-by-chunk explanation."""
        result = self.tool.execute(mode="compare", a="file2", b="file10")
        self.assertEqual(result["result"], -1)
        self.assertEqual(result["first_difference"], 1)
        self.assertEqual(result["chunks"][0], {"a": "file", "b": "file", "relation": "="})
        self.assertEqual(result["chunks"][1]["relation"], "<")
        self.assertEqual(result["chunks"][1]["a"], {"number": "2", "value": 2})
        self.assertEqual(result["chunks"][1]["b"], {"number": "10", "value": 10})

    def test_compare_equal_prefix_and_identity(self):
        """Verify prefix handling and fully equal comparisons."""
        prefix = self.tool.execute(mode="compare", a="file2", b="file2b")
        self.assertEqual(prefix["result"], -1)
        self.assertEqual(prefix["prefix_relation"], "a_is_prefix")
        self.assertIsNone(prefix["first_difference"])
        equal = self.tool.execute(mode="compare", a="a02", b="a2")
        self.assertEqual(equal["result"], 0)
        greater = self.tool.execute(mode="compare", a="a10", b="a2")
        self.assertEqual(greater["result"], 1)
        self.assertEqual(greater["first_difference"], 1)

    def test_compare_empty_string_is_a_prefix(self):
        """Verify the empty string reports a prefix relation, not a bare -1/1."""
        empty_first = self.tool.execute(mode="compare", a="", b="0.5")
        self.assertEqual(empty_first["result"], -1)
        self.assertEqual(empty_first["prefix_relation"], "a_is_prefix")
        self.assertIsNone(empty_first["first_difference"])
        empty_second = self.tool.execute(mode="compare", a="a", b="")
        self.assertEqual(empty_second["result"], 1)
        self.assertEqual(empty_second["prefix_relation"], "b_is_prefix")
        self.assertEqual(self.tool.execute(mode="compare", a="", b="")["result"], 0)

    def test_compare_first_difference_beyond_chunk_cap(self):
        """Verify first_difference is computed over the full chunk lists.

        The explanation list is capped by max_compare_chunks, but the verdict
        fields must never be derived from the truncated slice.
        """
        tool = NaturalSortTool(max_compare_chunks=2)
        result = tool.execute(mode="compare", a="a1b1", b="a1b2")
        self.assertEqual(result["result"], -1)
        self.assertTrue(result["chunks_truncated"])
        self.assertEqual(len(result["chunks"]), 2)
        self.assertEqual(result["first_difference"], 3)
        self.assertIsNone(result["prefix_relation"])

    # -- is_sorted mode --------------------------------------------------------

    def test_is_sorted_reports_violation_pairs(self):
        """Verify is_sorted returns adjacent violation pairs."""
        result = self.tool.execute(mode="is_sorted", items=["a1", "a10", "a2", "a3"])
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["sorted"])
        self.assertEqual(result["violations"], [["a10", "a2"]])
        clean = self.tool.execute(mode="is_sorted", items=["a1", "a2", "a10"])
        self.assertTrue(clean["sorted"])
        self.assertEqual(clean["violations"], [])

    def test_is_sorted_caps_violations(self):
        """Verify violations list is capped and the truncation flag is set."""
        tool = NaturalSortTool(max_violations=2)
        result = tool.execute(mode="is_sorted", items=["e", "d", "c", "b", "a"])
        self.assertEqual(len(result["violations"]), 2)
        self.assertTrue(result["violations_truncated"])

    # -- validation and caps ------------------------------------------------

    def test_invalid_mode_and_options(self):
        """Verify invalid modes and option values return structured errors."""
        for kwargs in (
            {"mode": "reverse"},
            {"mode": "sort", "items": ["a"], "case_sensitive": "yes"},
            {"mode": "sort", "items": ["a"], "number_mode": "fuzzy"},
            {"mode": "sort", "items": ["a"], "decimal": 1},
            {"mode": "sort", "items": ["a"], "unicode_digits": "expand"},
            {"mode": "sort", "items": ["a"], "leading_zeros": "zeroes"},
            {"mode": "sort"},
            {"mode": "compare", "a": "x"},
            {"mode": "compare", "b": "x"},
            {"mode": "rank", "value": "x"},
            {"mode": "rank", "value": "x", "reference": "not-a-list"},
        ):
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertTrue(result["error"])

    def test_items_must_be_strings(self):
        """Verify non-string items are rejected strictly, without coercion."""
        for bad in ([1], [None], [True], [["a"]], ["a", 2]):
            result = self.tool.execute(mode="sort", items=bad)
            self.assertEqual(result["status"], "error", bad)

    def test_list_size_and_item_length_caps(self):
        """Verify max_items and max_item_length are enforced."""
        tool = NaturalSortTool(max_items=2, max_item_length=3)
        self.assertEqual(tool.execute(mode="sort", items=["a", "b", "c"])["status"], "error")
        self.assertEqual(tool.execute(mode="sort", items=["abcd"])["status"], "error")
        self.assertEqual(tool.execute(mode="sort", items=["abc", "x0"])["status"], "success")

    def test_empty_list_sorts_to_empty(self):
        """Verify an empty items list succeeds with an empty result."""
        result = self.tool.execute(mode="sort", items=[])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["sorted"], [])
        self.assertEqual(result["swap_count"], 0)


class NaturalSortNatsortParityTest(unittest.TestCase):
    """Parity batteries against the natsort 8.4 reference oracle.

    natsort's defaults are case-SENSITIVE, while this tool's default is
    case-insensitive (casefold), so:
      * battery (a) pins our default against ``natsorted(x, alg=ns.IGNORECASE)``
        (natsort's IGNORECASE also casefolds: 'strasse' == 'straße'),
      * battery (b) pins our ``case_sensitive=True`` against plain
        ``natsorted(x)`` defaults.
    Both oracles and the tool use stable sorts and treat numerically equal
    leading-zero runs ('002' == '2') as equal keys, so orders must match
    exactly on every generated list.
    """

    def setUp(self):
        if not NATSORT_AVAILABLE:
            self.skipTest("natsort oracle not installed")
        self.tool = NaturalSortTool()

    @staticmethod
    def _battery_list(index):
        """Build seeded list #index across eight themed generators."""
        rng = random.Random(BATTERY_SEED + index)
        theme = index % 8
        size = rng.randint(5, 25)
        if theme == 0:  # filenames with numbers and extensions
            return [
                "{}{}{}{}".format(
                    rng.choice(["file", "img", "report", "note"]),
                    rng.choice(["_", "-", " ", " ("]),
                    str(rng.randint(0, 999)).zfill(rng.choice([1, 1, 3])),
                    rng.choice([".txt", ".md", ".png", ""]),
                )
                for _ in range(size)
            ]
        if theme == 1:  # version-like dotted numbers
            return [
                rng.choice([
                    ".".join(str(rng.randint(0, 50)) for _ in range(rng.randint(2, 4))),
                    "v{}".format(rng.randint(0, 50)),
                    "{}.{}".format(rng.randint(0, 9), rng.randint(0, 99)),
                ])
                for _ in range(size)
            ]
        if theme == 2:  # mixed-case words with numbers
            return [
                rng.choice(["Item", "ITEM", "item", "File", "FILE", "file"]) + str(rng.randint(0, 50))
                for _ in range(size)
            ]
        if theme == 3:  # CJK text with numbers
            return [
                rng.choice(["文件", "报告", "数据", "说明"]) + str(rng.randint(0, 50))
                + rng.choice(["", "_副本"])
                for _ in range(size)
            ]
        if theme == 4:  # empties and whitespace-padded tokens
            return [rng.choice(["", " ", "a", " a", "a ", " 1", "1 ", "2", "a1", "a 1"]) for _ in range(size)]
        if theme == 5:  # heavy duplicates from a tiny pool
            pool = ["a2", "a02", "a2b", "A2", "a10", "a1"]
            return [rng.choice(pool) for _ in range(size)]
        if theme == 6:  # very long digit runs (500-1000 digits)
            size = rng.randint(6, 10)
            return [
                str(rng.randint(0, 10 ** rng.randint(500, 1000)))
                if index % 2 else "9" * rng.randint(500, 1000)
                for _ in range(size)
            ]
        # theme 7: leading zeros
        return [
            "a" + str(rng.randint(0, 99)).zfill(rng.choice([1, 2, 3, 4]))
            for _ in range(size)
        ]

    def test_battery_a_default_matches_natsort_ignorecase(self):
        """Battery (a): default options must match natsorted(..., alg=ns.IGNORECASE)."""
        for index in range(BATTERY_LISTS):
            items = self._battery_list(index)
            result = self.tool.execute(mode="sort", items=items)
            self.assertEqual(result["status"], "success")
            self.assertEqual(
                result["sorted"],
                natsort.natsorted(items, alg=ns.IGNORECASE),
                f"battery (a) list #{index}: {items!r}",
            )

    def test_battery_b_case_sensitive_matches_natsort_default(self):
        """Battery (b): case_sensitive=True must match plain natsorted defaults."""
        for index in range(BATTERY_LISTS):
            items = self._battery_list(index)
            result = self.tool.execute(mode="sort", items=items, case_sensitive=True)
            self.assertEqual(result["status"], "success")
            self.assertEqual(
                result["sorted"],
                natsort.natsorted(items),
                f"battery (b) list #{index}: {items!r}",
            )

    def test_leading_zeros_pinned_against_natsort(self):
        """Pin default parity and the documented fewer_first divergence."""
        items = ["a002", "a2", "a02", "a2"]
        # natsort treats '002' == '2' as equal keys and keeps input order.
        self.assertEqual(self.tool.execute(mode="sort", items=items)["sorted"], natsort.natsorted(items))
        # fewer_first deliberately diverges: natsort has no equivalent option.
        self.assertEqual(
            self.tool.execute(mode="sort", items=["a002", "a2", "a02"], leading_zeros="fewer_first")["sorted"],
            ["a2", "a02", "a002"],
        )

    def test_unicode_digits_divergence_pinned(self):
        """Pin the documented default divergence: natsort normalizes Nd, we treat as text."""
        items = ["a3", "a1", "a٣"]
        self.assertEqual(natsort.natsorted(items), ["a1", "a3", "a٣"])  # both stable-equal tail
        self.assertEqual(self.tool.execute(mode="sort", items=items)["sorted"], ["a1", "a3", "a٣"])
        # Divergence becomes visible when the Nd digit's VALUE disagrees with
        # text ordering: natsort ranks 'a٣' between a2 and a4; text mode puts
        # it after every ASCII-digit sibling because '٣' compares as a letter.
        pair = ["a٤", "a3"]
        self.assertEqual(natsort.natsorted(pair), ["a3", "a٤"])
        self.assertEqual(self.tool.execute(mode="sort", items=pair)["sorted"], ["a3", "a٤"])
        pair = ["a٣", "a4"]
        self.assertEqual(natsort.natsorted(pair), ["a٣", "a4"])
        self.assertEqual(self.tool.execute(mode="sort", items=pair)["sorted"], ["a4", "a٣"])
        # normalize mode restores numeric treatment and matches natsort.
        self.assertEqual(
            self.tool.execute(mode="sort", items=["a٣", "a4"], unicode_digits="normalize")["sorted"],
            ["a٣", "a4"],
        )

    def test_casefold_parity_includes_sharp_s(self):
        """Pin that both natsort IGNORECASE and our default use casefold, not lower."""
        items = ["Weiß", "Weiss", "weis", "weiß"]
        self.assertEqual(
            self.tool.execute(mode="sort", items=items)["sorted"],
            natsort.natsorted(items, alg=ns.IGNORECASE),
        )

    def test_diacritics_match_natsort_nfd(self):
        """Verify text keys are NFD-normalized like the natsort oracle.

        natsort normalizes every string with Unicode NFD before comparing, so
        'café' sorts beside 'cafe' (the accent becomes a combining mark AFTER
        the base letter) and precomposed/decomposed forms are equal keys.
        Raw code-point comparison would put 'é' (U+00E9) after every ASCII
        letter, sorting 'CAFF' before 'café' — a visible oracle divergence.
        """
        for items in (
            ["café", "CAFF", "cafe", "CAFÉ"],
            ["réservé", "reserve", "zulu", "Réserve"],
            ["hôtel", "höz", "höz", "Hôtel", "haut"],
        ):
            self.assertEqual(
                self.tool.execute(mode="sort", items=items)["sorted"],
                natsort.natsorted(items, alg=ns.IGNORECASE),
                items,
            )
            self.assertEqual(
                self.tool.execute(mode="sort", items=items, case_sensitive=True)["sorted"],
                natsort.natsorted(items),
                items,
            )
        # Precomposed and decomposed accents are equal keys: input order kept.
        self.assertEqual(
            self.tool.execute(mode="sort", items=["cafe\u0301", "café"])["sorted"],
            ["cafe\u0301", "café"],
        )
        # Case-sensitive mode still NFD-normalizes (natsort does too).
        self.assertEqual(
            self.tool.execute(mode="compare", a="café", b="cafe\u0301")["result"], 0,
        )


class NaturalSortRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped natural_sort_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the NaturalSortTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "NaturalSortTool")

    def test_manager(self):
        """Verify the NaturalSortTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, NaturalSortTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
