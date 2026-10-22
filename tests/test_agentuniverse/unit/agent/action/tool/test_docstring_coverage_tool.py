#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_docstring_coverage_tool.py

"""Offline unit tests for DocstringCoverageTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic and checked against ground truths derived
independently of the tool's implementation: a hand-drawn matrix
covering every kind x visibility / dunder / override / property /
async / nested combination, hand-done summary arithmetic (counts,
1-decimal percentages, cap-at-50 truncation), hand-evaluated
threshold boundaries (>= semantics on the reported number), a
real-corpus pass over ten actual repository modules whose counts
were verified against their sources line by line, and a full
validation / syntax-error matrix.
"""

import pathlib
import sys
import unittest

from agentuniverse.agent.action.tool.common_tool import DocstringCoverageTool
from agentuniverse.agent.action.tool.common_tool.docstring_coverage_tool import (
    DocstringCoverageTool as DirectDocstringCoverageTool,
)


def summary_of(result):
    """The compact (module_docstring, total, documented, exempt, pct,
    by_kind) tuple of a summary result — for readable assertions."""
    return (
        result["module_docstring"],
        result["total_public"],
        result["documented_public"],
        result["exempt_public"],
        result["coverage_pct"],
        result["by_kind"],
    )


def undoc_of(result):
    """The ordered (qualname, line, kind) list of undocumented rows."""
    return [(row["qualname"], row["line"], row["kind"]) for row in result["undocumented"]]


# --------------------------------------------------------------------- #
# The matrix fixture: every kind x public/private/dunder/override/
# property/async/nested combination, one definition per marker line.
# Line numbers are read off the fixture below via ``line_of`` so the
# ground truth stays honest while the fixture stays readable.
# --------------------------------------------------------------------- #
MATRIX_LINES = [
    '"""Module overview docstring."""',  # 1
    "",  # 2
    "import functools",  # 3
    "from abc import abstractmethod",  # 4
    "from typing import TYPE_CHECKING, override",  # 5
    "",  # 6
    "def public_documented():",  # 7
    '    """Documented."""',  # 8
    "",  # 9
    "def public_missing():",  # 10
    "    pass",  # 11
    "",  # 12
    "async def async_public_missing(x: int | None) -> dict[str, int]:",  # 13
    "    return {}",  # 14
    "",  # 15
    "def _private_missing():",  # 16
    "    pass",  # 17
    "",  # 18
    "holder = lambda x: x  # lambdas are never rows",  # 19
    "",  # 20
    "def outer():",  # 21
    '    """Outer doc."""',  # 22
    "    def inner_public_name():",  # 23
    "        pass",  # 24
    "    return inner_public_name",  # 25
    "",  # 26
    "@functools.wraps(outer)",  # 27
    "def wrapper_no_doc():",  # 28
    "    pass",  # 29
    "",  # 30
    "@override",  # 31
    "def configured_override():",  # 32
    "    pass",  # 33
    "",  # 34
    "def pseudo_doc(x):",  # 35
    '    f"not {x} a docstring"',  # 36
    "",  # 37
    "if TYPE_CHECKING:",  # 38
    "    def conditional_def():",  # 39
    '        """Conditionally documented."""',  # 40
    "",  # 41
    "class Widget:",  # 42
    '    """Widget doc."""',  # 43
    "",  # 44
    "    def __init__(self):",  # 45
    "        pass",  # 46
    "",  # 47
    "    def use(self):",  # 48
    '        """Use doc."""',  # 49
    "",  # 50
    "    def drop(self):",  # 51
    "        pass",  # 52
    "",  # 53
    "    def _private_helper(self):",  # 54
    "        pass",  # 55
    "",  # 56
    "    @property",  # 57
    "    def size(self):",  # 58
    '        """Size doc."""',  # 59
    "",  # 60
    "    @size.setter",  # 61
    "    def size(self, value):",  # 62
    "        pass",  # 63
    "",  # 64
    "    @size.deleter",  # 65
    "    def size(self):",  # 66
    "        pass",  # 67
    "",  # 68
    "    @functools.cached_property",  # 69
    "    def cache_view(self):",  # 70
    "        pass",  # 71
    "",  # 72
    "    @setter_only.setter",  # 73
    "    def setter_only(self, value):",  # 74
    "        pass",  # 75
    "",  # 76
    "    @abstractmethod",  # 77
    "    def hook(self):",  # 78
    "        ...",  # 79
    "",  # 80
    "    @override",  # 81
    "    def close(self):",  # 82
    "        pass",  # 83
    "",  # 84
    "class Outer:",  # 85
    '    """Outer class doc."""',  # 86
    "",  # 87
    "    class Inner:",  # 88
    '        """Inner doc."""',  # 89
    "",  # 90
    "        def act(self):",  # 91
    "            pass",  # 92
    "",  # 93
    "def make():",  # 94
    '    """Make doc."""',  # 95
    "    class Local:",  # 96
    "        pass",  # 97
    "",  # 98
    "    return Local",  # 99
]
MATRIX = "\n".join(MATRIX_LINES)
MATRIX_NO_MODULE_DOC = "\n".join(["# a comment where the docstring should be", *MATRIX_LINES[1:]])


def line_of(marker):
    """The 1-based line number of the fixture line starting with
    ``marker`` — the ground-truth line numbers live next to the
    definitions they describe."""
    for number, line in enumerate(MATRIX_LINES, start=1):
        if line.startswith(marker):
            return number
    raise AssertionError(marker)


# Ground truth: qualname -> (kind, marker, has_docstring, is_public,
# is_nested, is_dunder, is_override, is_abstractmethod, is_wraps).
MATRIX_TRUTH = {
    "public_documented": ("function", "def public_documented", 1, 1, 0, 0, 0, 0, 0),
    "public_missing": ("function", "def public_missing", 0, 1, 0, 0, 0, 0, 0),
    "async_public_missing": ("function", "async def async_public_missing", 0, 1, 0, 0, 0, 0, 0),
    "_private_missing": ("function", "def _private_missing", 0, 0, 0, 0, 0, 0, 0),
    "outer": ("function", "def outer", 1, 1, 0, 0, 0, 0, 0),
    "outer.<locals>.inner_public_name": ("function", "    def inner_public_name", 0, 1, 1, 0, 0, 0, 0),
    "wrapper_no_doc": ("function", "def wrapper_no_doc", 0, 1, 0, 0, 0, 0, 1),
    "configured_override": ("function", "def configured_override", 0, 1, 0, 0, 1, 0, 0),
    "pseudo_doc": ("function", "def pseudo_doc", 0, 1, 0, 0, 0, 0, 0),
    "conditional_def": ("function", "    def conditional_def", 1, 1, 0, 0, 0, 0, 0),
    "Widget": ("class", "class Widget", 1, 1, 0, 0, 0, 0, 0),
    "Widget.__init__": ("method", "    def __init__", 0, 0, 0, 1, 0, 0, 0),
    "Widget.use": ("method", "    def use", 1, 1, 0, 0, 0, 0, 0),
    "Widget.drop": ("method", "    def drop", 0, 1, 0, 0, 0, 0, 0),
    "Widget._private_helper": ("method", "    def _private_helper", 0, 0, 0, 0, 0, 0, 0),
    "Widget.size": ("method", "    def size", 1, 1, 0, 0, 0, 0, 0),
    "Widget.cache_view": ("method", "    def cache_view", 0, 1, 0, 0, 0, 0, 0),
    "Widget.setter_only": ("method", "    def setter_only", 0, 1, 0, 0, 0, 0, 0),
    "Widget.hook": ("method", "    def hook", 0, 1, 0, 0, 0, 1, 0),
    "Widget.close": ("method", "    def close", 0, 1, 0, 0, 1, 0, 0),
    "Outer": ("class", "class Outer", 1, 1, 0, 0, 0, 0, 0),
    "Outer.Inner": ("class", "    class Inner", 1, 1, 0, 0, 0, 0, 0),
    "Outer.Inner.act": ("method", "        def act", 0, 1, 0, 0, 0, 0, 0),
    "make": ("function", "def make", 1, 1, 0, 0, 0, 0, 0),
    "make.<locals>.Local": ("class", "    class Local", 0, 1, 1, 0, 0, 0, 0),
}

# Hand-derived summary over the matrix (see the module docstring):
# requiring rows are the public, non-nested, non-exempt ones —
#   functions : public_documented, outer, conditional_def, make
#               documented; public_missing, async_public_missing,
#               pseudo_doc not                 -> 7 total, 4 documented
#   classes   : Widget, Outer, Outer.Inner     -> 3 total, 3 documented
#   methods   : use, size documented; drop, cache_view,
#               setter_only, Outer.Inner.act   -> 6 total, 2 documented
# exempt public rows: wrapper_no_doc, configured_override,
#                     Widget.hook, Widget.close -> 4
# 9 documented / 16 requiring = 56.25 -> 56.2 (the exact half rounds
# half-to-even, which Python's round does deterministically)
MATRIX_SUMMARY = {
    "module_docstring": True,
    "total_public": 16,
    "documented_public": 9,
    "exempt_public": 4,
    "coverage_pct": 56.2,
    "by_kind": {
        "function": {"total": 7, "documented": 4},
        "class": {"total": 3, "documented": 3},
        "method": {"total": 6, "documented": 2},
    },
    "undocumented_total": 7,
}
MATRIX_UNDOCUMENTED = [
    ("public_missing", line_of("def public_missing"), "function"),
    ("async_public_missing", line_of("async def async_public_missing"), "function"),
    ("pseudo_doc", line_of("def pseudo_doc"), "function"),
    ("Widget.drop", line_of("    def drop"), "method"),
    ("Widget.cache_view", line_of("    def cache_view"), "method"),
    ("Widget.setter_only", line_of("    def setter_only"), "method"),
    ("Outer.Inner.act", line_of("        def act"), "method"),
]


class ScanMatrixTest(unittest.TestCase):
    """scan mode over the full hand-drawn matrix."""

    def setUp(self):
        self.tool = DocstringCoverageTool()
        self.result = self.tool.execute(mode="scan", text=MATRIX)
        self.rows = {row["qualname"]: row for row in self.result["items"]}

    def test_module_docstring_flag(self):
        self.assertTrue(self.result["module_docstring"])
        without = self.tool.execute(mode="scan", text=MATRIX_NO_MODULE_DOC)
        self.assertFalse(without["module_docstring"])
        self.assertEqual(
            [row["qualname"] for row in without["items"]],
            [row["qualname"] for row in self.result["items"]],
        )

    def test_every_kind_and_flag_combination(self):
        self.assertEqual(
            sorted(self.rows),
            sorted(MATRIX_TRUTH),
            "the inventory must contain exactly the ground-truth rows",
        )
        for qualname, truth in MATRIX_TRUTH.items():
            kind, marker, has_doc, public, nested, dunder, override, abstract, wraps = truth
            row = self.rows[qualname]
            self.assertEqual(row["kind"], kind, qualname)
            self.assertEqual(row["line"], line_of(marker), qualname)
            self.assertEqual(row["has_docstring"], bool(has_doc), qualname)
            self.assertEqual(row["is_public"], bool(public), qualname)
            self.assertEqual(row["is_nested"], bool(nested), qualname)
            self.assertEqual(row["is_dunder"], bool(dunder), qualname)
            self.assertEqual(row["is_override"], bool(override), qualname)
            self.assertEqual(row["is_abstractmethod"], bool(abstract), qualname)
            self.assertEqual(row["is_wraps"], bool(wraps), qualname)
            self.assertEqual(row["exempt"], bool(override or abstract or wraps), qualname)

    def test_items_sorted_by_line(self):
        lines = [row["line"] for row in self.result["items"]]
        self.assertEqual(lines, sorted(lines))

    def test_property_pair_counted_once(self):
        size_rows = [r for r in self.result["items"] if r["qualname"] == "Widget.size"]
        self.assertEqual(len(size_rows), 1, "getter+setter+deleter = one row")
        self.assertEqual(size_rows[0]["line"], line_of("    def size"))
        self.assertTrue(size_rows[0]["has_docstring"])

    def test_lambdas_skipped_and_async_counted(self):
        self.assertNotIn("holder", self.rows)
        self.assertNotIn("<lambda>", self.rows)
        self.assertIn("async_public_missing", self.rows)

    def test_row_schema_is_fixed(self):
        expected = {
            "kind",
            "qualname",
            "line",
            "has_docstring",
            "is_public",
            "is_nested",
            "is_dunder",
            "is_override",
            "is_abstractmethod",
            "is_wraps",
            "exempt",
        }
        for row in self.result["items"]:
            self.assertEqual(set(row), expected)

    def test_scan_cap_truncates(self):
        source = "\n".join(f"def f{i}():\n    pass" for i in range(self.tool.max_items + 5))
        result = self.tool.execute(mode="scan", text=source)
        self.assertTrue(result["items_truncated"])
        self.assertEqual(result["items_total"], self.tool.max_items + 5)
        self.assertEqual(len(result["items"]), self.tool.max_items)


class SummaryArithmeticTest(unittest.TestCase):
    """summary mode — hand-verified counts, rounding and caps."""

    def setUp(self):
        self.tool = DocstringCoverageTool()

    def test_matrix_summary(self):
        result = self.tool.execute(mode="summary", text=MATRIX)
        for key, expected in MATRIX_SUMMARY.items():
            self.assertEqual(result[key], expected, key)
        self.assertEqual(undoc_of(result), MATRIX_UNDOCUMENTED)
        self.assertFalse(result["truncated"])
        self.assertEqual(len(result["undocumented"]), result["undocumented_total"])

    def test_empty_module_is_vacuously_complete(self):
        result = self.tool.execute(mode="summary", text="# only a comment\n")
        self.assertEqual(
            summary_of(result),
            (
                False,
                0,
                0,
                0,
                100.0,
                {
                    "function": {"total": 0, "documented": 0},
                    "class": {"total": 0, "documented": 0},
                    "method": {"total": 0, "documented": 0},
                },
            ),
        )

    def test_rounding_to_one_decimal(self):
        # 2/3 documented = 66.666...% -> 66.7 ; 1/6 -> 16.7 ; 5/8 -> 62.5
        thirds = "def a():\n    'd'\n\n\ndef b():\n    'd'\n\n\ndef c():\n    pass"
        self.assertEqual(self.tool.execute(mode="summary", text=thirds)["coverage_pct"], 66.7)
        sixths = "\n\n".join(["def a():\n    'd'"] + [f"def f{i}():\n    pass" for i in range(5)])
        self.assertEqual(self.tool.execute(mode="summary", text=sixths)["coverage_pct"], 16.7)
        eighths = "\n\n".join(["def a():\n    'd'"] * 5 + [f"def f{i}():\n    pass" for i in range(3)])
        self.assertEqual(self.tool.execute(mode="summary", text=eighths)["coverage_pct"], 62.5)

    def test_undocumented_cap_at_50(self):
        # 55 public undocumented functions: the list keeps the first 50
        # by line, the totals keep the true count.
        source = "\n".join(f"def f{i:02d}():\n    pass" for i in range(55))
        result = self.tool.execute(mode="summary", text=source)
        self.assertEqual(result["total_public"], 55)
        self.assertEqual(result["documented_public"], 0)
        self.assertEqual(result["coverage_pct"], 0.0)
        self.assertEqual(result["undocumented_total"], 55)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["undocumented"]), 50)
        self.assertEqual(result["undocumented"][0]["qualname"], "f00")
        self.assertEqual(result["undocumented"][49]["qualname"], "f49")

    def test_undocumented_sorted_by_line(self):
        result = self.tool.execute(mode="summary", text=MATRIX)
        lines = [row["line"] for row in result["undocumented"]]
        self.assertEqual(lines, sorted(lines))

    def test_exempt_items_leave_the_requirement(self):
        # All four exempt rows are public; none may drag coverage down.
        result = self.tool.execute(mode="summary", text=MATRIX)
        self.assertEqual(result["exempt_public"], 4)
        self.assertNotIn("Widget.hook", [row["qualname"] for row in result["undocumented"]])

    def test_nested_and_private_leave_the_requirement(self):
        result = self.tool.execute(mode="summary", text=MATRIX)
        names = [row["qualname"] for row in result["undocumented"]]
        self.assertNotIn("outer.<locals>.inner_public_name", names)
        self.assertNotIn("make.<locals>.Local", names)
        self.assertNotIn("Widget.__init__", names)
        self.assertNotIn("Widget._private_helper", names)


class CheckThresholdTest(unittest.TestCase):
    """check mode — pass/fail per threshold, boundaries, offenders."""

    def setUp(self):
        self.tool = DocstringCoverageTool()

    def checks_of(self, **kwargs):
        result = self.tool.execute(mode="check", text=MATRIX, **kwargs)
        return result, {entry["check"]: entry for entry in result["checks"]}

    def test_defaults_pass_everything(self):
        result, checks = self.checks_of()
        self.assertTrue(result["passed"])
        self.assertEqual(result["thresholds"], {"min_module": 0, "min_public": 0.0, "min_class": 0.0})
        for entry in checks.values():
            self.assertTrue(entry["passed"])
            self.assertEqual(entry["offenders"], [])

    def test_module_gate(self):
        result, checks = self.checks_of(min_module=1)
        self.assertTrue(checks["module_docstring"]["passed"])
        self.assertTrue(result["passed"])
        result = self.tool.execute(mode="check", text=MATRIX_NO_MODULE_DOC, min_module=1)
        entry = result["checks"][0]
        self.assertEqual(entry["check"], "module_docstring")
        self.assertFalse(entry["passed"])
        self.assertEqual(entry["offenders"], [{"qualname": "<module>", "line": 1, "kind": "module"}])
        self.assertFalse(result["passed"])

    def test_public_coverage_boundary_is_inclusive(self):
        # Matrix coverage is exactly 56.2 (reported); >= passes, above fails.
        _, checks = self.checks_of(min_public=56.2)
        self.assertTrue(checks["public_coverage"]["passed"])
        self.assertEqual(checks["public_coverage"]["coverage_pct"], 56.2)
        _, checks = self.checks_of(min_public=56.21)
        self.assertFalse(checks["public_coverage"]["passed"])

    def test_class_gate_is_classes_plus_methods(self):
        # Class surface on the matrix: (3 classes + 6 methods) with
        # (3 + 2) documented -> 5/9 = 55.555... -> 55.6.
        result, checks = self.checks_of(min_class=55.6)
        entry = checks["class_coverage"]
        self.assertEqual(entry["coverage_pct"], 55.6)
        self.assertTrue(result["passed"])
        self.assertTrue(entry["passed"])
        self.assertEqual(entry["offenders"], [])
        _, checks = self.checks_of(min_class=55.7)
        entry = checks["class_coverage"]
        self.assertFalse(entry["passed"])
        self.assertEqual(
            [row["qualname"] for row in entry["offenders"]],
            ["Widget.drop", "Widget.cache_view", "Widget.setter_only", "Outer.Inner.act"],
        )
        self.assertEqual(entry["undocumented_total"], 4)

    def test_class_gate_independent_of_public_gate(self):
        # One documented function plus a bare class: overall coverage
        # is 1/3 = 33.3% (clears min_public=30) while the class
        # surface is 0/2 = 0.0% (fails min_class=50).
        source = "\n".join(
            [
                '"""Doc."""',
                "def fine():",
                '    "d"',
                "class Bare:",
                "    def act(self):",
                "        pass",
            ]
        )
        result = self.tool.execute(mode="check", text=source, min_public=30, min_class=50)
        checks = {entry["check"]: entry for entry in result["checks"]}
        self.assertTrue(checks["public_coverage"]["passed"])
        self.assertFalse(checks["class_coverage"]["passed"])
        self.assertFalse(result["passed"])

    def test_vacuous_class_surface_passes(self):
        result = self.tool.execute(mode="check", text="def only_a_function():\n    'd'\n", min_class=100)
        entry = result["checks"][2]
        self.assertEqual(entry["coverage_pct"], 100.0)
        self.assertTrue(entry["passed"])

    def test_offenders_only_listed_when_failing(self):
        _, checks = self.checks_of(min_public=56.2, min_class=55.6)
        self.assertEqual(checks["public_coverage"]["offenders"], [])
        self.assertEqual(checks["class_coverage"]["offenders"], [])

    def test_offenders_capped_at_50(self):
        source = "\n".join(f"def f{i:02d}():\n    pass" for i in range(55))
        result = self.tool.execute(mode="check", text=source, min_public=1)
        entry = result["checks"][1]
        self.assertFalse(entry["passed"])
        self.assertEqual(len(entry["offenders"]), 50)
        self.assertEqual(entry["undocumented_total"], 55)

    def test_passed_is_the_conjunction(self):
        result = self.tool.execute(mode="check", text=MATRIX_NO_MODULE_DOC, min_module=1, min_public=99)
        self.assertFalse(result["passed"])
        self.assertEqual([entry["passed"] for entry in result["checks"]], [False, False, True])

    def test_integer_and_boolean_thresholds(self):
        self.assertTrue(self.tool.execute(mode="check", text=MATRIX, min_module=True)["passed"])
        self.assertTrue(self.tool.execute(mode="check", text=MATRIX, min_public=100 / 3)["passed"])
        self.assertTrue(self.tool.execute(mode="check", text=MATRIX, min_class=55)["passed"])


class SyntaxErrorTest(unittest.TestCase):
    """Unparsable source returns a structured payload, never raises."""

    def setUp(self):
        self.tool = DocstringCoverageTool()

    def test_syntax_error_payload(self):
        result = self.tool.execute(mode="scan", text="def broken(:\n    pass\n")
        self.assertEqual(result["mode"], "scan")
        self.assertEqual(result["error"]["type"], "syntax_error")
        self.assertEqual(result["error"]["line"], 1)
        self.assertIsNotNone(result["error"]["offset"])
        self.assertEqual(result["error"]["text"], "def broken(:")
        self.assertIn("invalid syntax", result["error"]["message"])

    def test_syntax_error_line_points_at_the_problem(self):
        result = self.tool.execute(mode="summary", text="def ok():\n    pass\n\nclass oops(:\n    pass\n")
        self.assertEqual(result["error"]["type"], "syntax_error")
        self.assertEqual(result["error"]["line"], 4)

    def test_null_bytes_are_a_content_error(self):
        result = self.tool.execute(mode="check", text="def a():\x00\n    pass\n")
        self.assertEqual(result["error"]["type"], "syntax_error")
        self.assertEqual(result["error"]["line"], None)

    def test_error_preview_capped_at_60_chars(self):
        bad = "x " + "y" * 100 + " !"
        result = self.tool.execute(mode="scan", text=bad)
        self.assertLessEqual(len(result["error"]["text"]), 63)
        self.assertTrue(result["error"]["text"].endswith("..."))

    def test_leading_bom_is_tolerated_like_the_importer(self):
        # CPython loads BOM-prefixed files; the audit must too.
        result = self.tool.execute(mode="summary", text="\ufeff" + '"""Doc."""\n\ndef f():\n    "d"\n')
        self.assertTrue(result["module_docstring"])
        self.assertEqual(result["coverage_pct"], 100.0)


class ValidationTest(unittest.TestCase):
    """The full parameter-validation error matrix."""

    def setUp(self):
        self.tool = DocstringCoverageTool()

    def assert_invalid(self, message_part, **kwargs):
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(**kwargs)
        self.assertIn("docstring_coverage_tool:", str(caught.exception))
        self.assertIn(message_part, str(caught.exception))

    def test_mode(self):
        self.assert_invalid("mode must be one of", mode="audit", text="x = 1")
        self.assert_invalid("mode must be one of", mode=None, text="x = 1")
        self.assert_invalid("mode must be one of", mode=1, text="x = 1")

    def test_text_type(self):
        for bad in (None, True, 42, ["x"], {"a": 1}):
            self.assert_invalid("text must be a non-empty string", mode="scan", text=bad)

    def test_text_empty(self):
        self.assert_invalid("text must be a non-empty string", mode="scan", text="")
        self.assert_invalid("text must be a non-empty string", mode="scan", text="  \n\t ")

    def test_text_too_large(self):
        self.assert_invalid("10,000,000-character limit", mode="scan", text="x" * 10_000_001)

    def test_thresholds_rejected_outside_check(self):
        for mode in ("scan", "summary"):
            for option in ("min_module", "min_public", "min_class"):
                self.assert_invalid(
                    f"{option} is only accepted in check mode",
                    mode=mode,
                    text="x = 1",
                    **{option: 1},
                )

    def test_min_module_values(self):
        for bad in (2, -1, "1", 1.0):
            self.assert_invalid(
                "min_module must be 0 or 1",
                mode="check",
                text="x = 1",
                min_module=bad,
            )

    def test_min_public_values(self):
        for bad in ("80", True, -0.1, 100.5, [80]):
            self.assert_invalid(
                "min_public must be a number from 0 to 100",
                mode="check",
                text="x = 1",
                min_public=bad,
            )

    def test_min_class_values(self):
        for bad in (-1, 101, "x", False):
            self.assert_invalid(
                "min_class must be a number from 0 to 100",
                mode="check",
                text="x = 1",
                min_class=bad,
            )

    def test_boundary_values_accepted(self):
        for good in (0, 100, 0.0, 100.0, 53.3):
            self.tool.execute(mode="check", text="x = 1", min_public=good)
        for good in (0, 1, True, False):
            self.tool.execute(mode="check", text="x = 1", min_module=good)


# Ground truths for the real corpus: module path ->
# (module_docstring, total_public, documented_public, exempt_public,
#  coverage_pct, {kind: (total, documented)}). Every def/class line of
# these ten modules was inspected to derive the numbers.
CORPUS_TRUTH = {
    "agentuniverse/__init__.py": (
        False,
        0,
        0,
        0,
        100.0,
        {"function": (0, 0), "class": (0, 0), "method": (0, 0)},
    ),
    "agentuniverse/base/util/env_util.py": (
        False,
        1,
        1,
        0,
        100.0,
        {"function": (1, 1), "class": (0, 0), "method": (0, 0)},
    ),
    "agentuniverse/base/util/system_util.py": (
        False,
        8,
        8,
        0,
        100.0,
        {"function": (8, 8), "class": (0, 0), "method": (0, 0)},
    ),
    "agentuniverse/agent/action/tool/tool.py": (
        False,
        19,
        12,
        1,
        63.2,
        {"function": (0, 0), "class": (2, 2), "method": (17, 10)},
    ),
    "agentuniverse/agent/action/tool/common_tool/simple_math_tool.py": (
        False,
        12,
        12,
        0,
        100.0,
        {"function": (0, 0), "class": (4, 4), "method": (8, 8)},
    ),
    "agentuniverse/agent/action/tool/common_tool/python_repl.py": (
        False,
        2,
        2,
        0,
        100.0,
        {"function": (0, 0), "class": (1, 1), "method": (1, 1)},
    ),
    "agentuniverse/agent/action/tool/common_tool/mock_search_tool.py": (
        False,
        4,
        1,
        0,
        25.0,
        {"function": (0, 0), "class": (1, 1), "method": (3, 0)},
    ),
    "agentuniverse/agent/action/tool/common_tool/bing_search_tool.py": (
        False,
        2,
        1,
        0,
        50.0,
        {"function": (0, 0), "class": (1, 1), "method": (1, 0)},
    ),
    "agentuniverse/agent/action/tool/common_tool/wikipedia_query.py": (
        False,
        2,
        0,
        0,
        0.0,
        {"function": (0, 0), "class": (1, 0), "method": (1, 0)},
    ),
    "agentuniverse/agent/action/tool/common_tool/write_file_tool.py": (
        False,
        2,
        0,
        0,
        0.0,
        {"function": (0, 0), "class": (1, 0), "method": (1, 0)},
    ),
}


class RealCorpusTest(unittest.TestCase):
    """Ten actual repository modules; counts verified against the
    sources by hand (every def/class line was inspected)."""

    @classmethod
    def setUpClass(cls):
        cls.tool = DocstringCoverageTool()
        cls.root = pathlib.Path(__file__).resolve()
        while not (cls.root / "agentuniverse" / "__init__.py").exists():
            if cls.root.parent == cls.root:
                raise AssertionError("repository root not found")
            cls.root = cls.root.parent

    def test_spot_verified_counts(self):
        for relative, truth in CORPUS_TRUTH.items():
            with self.subTest(module=relative):
                source = (self.root / relative).read_text(encoding="utf-8")
                module_doc, total, documented, exempt, pct, kinds = truth
                result = self.tool.execute(mode="summary", text=source)
                self.assertEqual(result["module_docstring"], module_doc)
                self.assertEqual(result["total_public"], total)
                self.assertEqual(result["documented_public"], documented)
                self.assertEqual(result["exempt_public"], exempt)
                self.assertEqual(result["coverage_pct"], pct)
                self.assertEqual(
                    result["by_kind"],
                    {kind: {"total": pair[0], "documented": pair[1]} for kind, pair in kinds.items()},
                )

    def test_tool_py_undocumented_names(self):
        # Hand-checked against the source: exactly these seven public
        # methods lack docstrings; Tool.execute is the @abstractmethod
        # (the one exemption).
        source = (self.root / "agentuniverse/agent/action/tool/tool.py").read_text(encoding="utf-8")
        result = self.tool.execute(mode="summary", text=source)
        self.assertEqual(
            [row["qualname"] for row in result["undocumented"]],
            [
                "ToolInput.to_dict",
                "ToolInput.to_json_str",
                "ToolInput.add_data",
                "ToolInput.get_data",
                "Tool.async_langchain_run",
                "Tool.async_as_langchain",
                "Tool.create_copy",
            ],
        )

    def test_scan_invariants_over_corpus(self):
        for relative in CORPUS_TRUTH:
            with self.subTest(module=relative):
                source = (self.root / relative).read_text(encoding="utf-8")
                scan = self.tool.execute(mode="scan", text=source)
                lines = [row["line"] for row in scan["items"]]
                self.assertEqual(lines, sorted(lines))
                qualnames = [row["qualname"] for row in scan["items"]]
                self.assertEqual(len(qualnames), len(set(qualnames)))
                for row in scan["items"]:
                    self.assertIn(row["kind"], ("function", "class", "method"))

    def test_deterministic_across_calls(self):
        for relative in CORPUS_TRUTH:
            with self.subTest(module=relative):
                source = (self.root / relative).read_text(encoding="utf-8")
                for mode in ("scan", "summary"):
                    self.assertEqual(
                        self.tool.execute(mode=mode, text=source),
                        self.tool.execute(mode=mode, text=source),
                    )
                self.assertEqual(
                    self.tool.execute(mode="check", text=source, min_module=1, min_public=50),
                    self.tool.execute(mode="check", text=source, min_module=1, min_public=50),
                )


class RegistrationTest(unittest.TestCase):
    """The tool is importable through the package __init__ and wired
    to its component yaml."""

    def test_class_identity(self):
        self.assertIs(DocstringCoverageTool, DirectDocstringCoverageTool)

    def test_tool_metadata(self):
        tool = DocstringCoverageTool()
        self.assertEqual(tool.name, "docstring_coverage_tool")
        self.assertEqual(tool.MODES, ("scan", "summary", "check"))

    def test_yaml_wiring(self):
        import yaml

        root = pathlib.Path(__file__).resolve()
        while not (root / "agentuniverse" / "__init__.py").exists():
            root = root.parent
        path = root / "agentuniverse" / "agent" / "action" / "tool" / "common_tool" / "docstring_coverage_tool.yaml"
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(config["name"], "docstring_coverage_tool")
        self.assertEqual(config["input_keys"], ["mode", "text"])
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.docstring_coverage_tool",
        )
        self.assertEqual(config["metadata"]["class"], "DocstringCoverageTool")
        self.assertEqual(sorted(config["args_model_schema"]["required"]), ["mode", "text"])


class HostileReviewRegressionTest(unittest.TestCase):
    """Regressions for defects found in the hostile self-review:

    1. ``try ... except*`` suites (ast.TryStar, Python 3.11+) were not
       flattened, so definitions inside an except-group block silently
       vanished from the audit (scan, summary and check all missed them).
    2. The documented size caps (max_text_chars / max_items /
       max_undocumented) were ClassVars, not model fields:
       ``tool.max_items = 5`` raised AttributeError and the constructor
       kwarg was silently ignored — dead config.
    3. Validation errors echoed the rejected value with unbounded repr
       (a megabyte ``mode`` string produced a megabyte error message).
    4. The 1-decimal rounding convention (half-to-even on exact halves)
       was pinned only in this file's comments, not in the tool's
       documentation.
    """

    def setUp(self):
        self.tool = DocstringCoverageTool()

    def test_except_star_definitions_are_audited(self):
        # A public def inside an except* block belongs to the module
        # scope exactly like one inside a plain except handler.
        if sys.version_info < (3, 11):
            self.skipTest("except* requires Python 3.11+")
        source = "\n".join(
            [
                '"""Doc."""',
                "try:",
                "    pass",
                "except* ValueError:",
                "    def fallback():",
                '        """Handled."""',
                "try:",
                "    pass",
                "except TypeError:",
                "    def except_def():",
                "        pass",
            ]
        )
        scan = self.tool.execute(mode="scan", text=source)
        self.assertEqual(
            [(row["qualname"], row["has_docstring"]) for row in scan["items"]],
            [("fallback", True), ("except_def", False)],
        )
        summary = self.tool.execute(mode="summary", text=source)
        self.assertEqual(summary["total_public"], 2)
        self.assertEqual(summary["documented_public"], 1)
        self.assertEqual(summary["coverage_pct"], 50.0)
        check = self.tool.execute(mode="check", text=source, min_public=51)
        self.assertFalse(check["passed"])
        self.assertEqual(
            [row["qualname"] for row in check["checks"][1]["offenders"]],
            ["except_def"],
        )
        # Inside a class body too: except* defs are methods of the class.
        class_src = "\n".join(
            [
                "class Handler:",
                "    try:",
                "        pass",
                "    except* ValueError:",
                "        def handle(self):",
                "            pass",
            ]
        )
        scan = self.tool.execute(mode="scan", text=class_src)
        self.assertEqual(
            [(row["qualname"], row["kind"]) for row in scan["items"]],
            [("Handler", "class"), ("Handler.handle", "method")],
        )

    def test_caps_are_live_model_fields(self):
        # Documented Attributes must be real fields: assignment must not
        # raise and must take effect; constructor kwargs must not be
        # silently swallowed.
        self.assertIn("max_undocumented", DocstringCoverageTool.model_fields)
        self.assertIn("max_items", DocstringCoverageTool.model_fields)
        self.assertIn("max_text_chars", DocstringCoverageTool.model_fields)
        source = "\n".join(f"def f{i:02d}():\n    pass" for i in range(10))
        tool = DocstringCoverageTool()
        tool.max_undocumented = 3
        result = tool.execute(mode="summary", text=source)
        self.assertEqual(len(result["undocumented"]), 3)
        self.assertEqual(result["undocumented_total"], 10)
        self.assertTrue(result["truncated"])
        tool.max_items = 5
        scan = tool.execute(mode="scan", text=source)
        self.assertEqual(scan["items_total"], 10)
        self.assertEqual(len(scan["items"]), 5)
        self.assertTrue(scan["items_truncated"])
        ctor = DocstringCoverageTool(max_undocumented=2)
        self.assertEqual(len(ctor.execute(mode="summary", text=source)["undocumented"]), 2)

    def test_caps_validation(self):
        from pydantic import ValidationError

        for bad in (0, -1):
            with self.assertRaises(ValidationError):
                DocstringCoverageTool(max_items=bad, max_text_chars=bad)
        with self.assertRaises(ValidationError):
            DocstringCoverageTool(max_undocumented=-1)
        # max_undocumented=0 (list nothing, keep the totals) is legal.
        tool = DocstringCoverageTool(max_undocumented=0)
        result = tool.execute(mode="summary", text="def f():\n    pass\n")
        self.assertEqual(result["undocumented"], [])
        self.assertEqual(result["undocumented_total"], 1)

    def test_error_echo_is_bounded(self):
        # A megabyte of bad input must not produce a megabyte of message.
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(mode="x" * 1_000_000, text="pass")
        self.assertLess(len(str(caught.exception)), 200)

        class HugeRepr:
            def __repr__(self):
                return "R" * 2_000_000

        with self.assertRaises(ValueError) as caught:
            self.tool.execute(mode="scan", text=HugeRepr())
        self.assertLess(len(str(caught.exception)), 200)
        for option in ("min_module", "min_public", "min_class"):
            with self.assertRaises(ValueError) as caught:
                self.tool.execute(mode="check", text="pass", **{option: HugeRepr()})
            self.assertLess(len(str(caught.exception)), 200)
        # Small invalid values are still echoed readably.
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(mode="check", text="pass", min_public="eighty")
        self.assertIn("'eighty'", str(caught.exception))

    def test_rounding_is_half_to_even_and_pinned(self):
        # Exact binary halves at the second decimal: round() rounds
        # half-to-even (56.25 -> 56.2, 74.25 -> 74.2, 0.75 -> 0.8),
        # NOT decimal half-up (which would give 56.3 / 74.3 / 0.8).
        def module(documented, total):
            parts = [f"def d{i}():\n    'x'" for i in range(documented)]
            parts += [f"def u{i}():\n    pass" for i in range(total - documented)]
            return "\n".join(parts)

        for documented, total, expected in (
            (9, 16, 56.2),  # 56.25 exact: half-to-even down (2 is even)
            (221, 400, 55.2),  # 55.25 exact: half-to-even down
            (297, 400, 74.2),  # 74.25 exact
            (3, 400, 0.8),  # 0.75 exact: half-to-even up (7 is odd)
            (1, 16, 6.2),  # 6.25 exact
        ):
            with self.subTest(documented=documented, total=total):
                result = self.tool.execute(mode="summary", text=module(documented, total))
                self.assertEqual(result["coverage_pct"], expected)
        # The gate sees the reported number: 55.2 passes at 55.2, fails at 55.3.
        source = module(221, 400)
        self.assertTrue(self.tool.execute(mode="check", text=source, min_public=55.2)["checks"][1]["passed"])
        self.assertFalse(self.tool.execute(mode="check", text=source, min_public=55.3)["checks"][1]["passed"])

    def test_guidebook_sections_present(self):
        root = pathlib.Path(__file__).resolve()
        while not (root / "agentuniverse" / "__init__.py").exists():
            root = root.parent
        for relative in (
            "docs/guidebook/en/In-Depth_Guides/Components/Tools/Integrated_Tools.md",
            "docs/guidebook/zh/In-Depth_Guides/组件列表/工具列表/集成的工具.md",
        ):
            with self.subTest(doc=relative):
                text = (root / relative).read_text(encoding="utf-8")
                self.assertIn("DocstringCoverageTool", text)


if __name__ == "__main__":
    unittest.main()
