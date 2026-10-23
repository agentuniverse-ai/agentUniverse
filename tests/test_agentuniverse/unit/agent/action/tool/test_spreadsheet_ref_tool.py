"""Oracle-based unit tests for SpreadsheetRefTool.

Every randomized suite is checked against an independent implementation
written inside this file (positional power-sum column math, a character
level tokenizer for formulas, brute-force cell-set algebra), never
against the tool's own code paths.
"""

import os
import random
import re
import unittest

from agentuniverse.agent.action.tool.common_tool import spreadsheet_ref_tool as sheetref_module
from agentuniverse.agent.action.tool.common_tool.spreadsheet_ref_tool import SpreadsheetRefTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(sheetref_module.__file__), "spreadsheet_ref_tool.yaml")

MAX_ROW, MAX_COL = 1048576, 16384


# ---------------------------------------------------------------------------
# Independent oracles (deliberately different formulations from the tool)
# ---------------------------------------------------------------------------
def oracle_letters_to_index(letters):
    """Positional power-sum column math, independent of the tool's loop form."""
    return sum(
        (ord(char) - 64) * 26 ** (len(letters) - position - 1)
        for position, char in enumerate(letters.upper())
    )


def oracle_index_to_letters(index):
    """Recursive bijective base-26 rendering."""
    if index == 0:
        return ""
    return oracle_index_to_letters((index - 1) // 26) + chr(65 + (index - 1) % 26)


A1_TOKEN_RE = re.compile(r"^(\$?)([A-Za-z]{1,3})(\$?)([0-9]+)$")


def oracle_parse_a1(token):
    """Independent A1 parse returning (row, col, abs_row, abs_col) or None."""
    match = A1_TOKEN_RE.match(token)
    if not match:
        return None
    col = oracle_letters_to_index(match.group(2))
    row = int(match.group(4))
    if row < 1 or row > MAX_ROW or col < 1 or col > MAX_COL:
        return None
    return row, col, match.group(3) == "$", match.group(1) == "$"


def oracle_cells_of(ref):
    """Brute-force cell set of an A1 range string like 'A1:B2' (small ranges)."""
    left, _, right = ref.partition(":")
    if not right:
        right = left
    r1, c1, _, _ = oracle_parse_a1(left)
    r2, c2, _, _ = oracle_parse_a1(right)
    return {
        (row, col)
        for row in range(min(r1, r2), max(r1, r2) + 1)
        for col in range(min(c1, c2), max(c1, c2) + 1)
    }


def oracle_formula_refs(formula):
    """Independent character-level tokenizer for extract_refs.

    Returns ref strings (with any sheet prefix attached). Skips
    double-quoted strings (honoring Excel's doubled-quote escaping) and
    single-quoted sheet names; a token counts as a reference only when
    it parses under the A1 grammar, is not glued to identifier
    characters, and is not immediately followed by '('.
    """
    refs = []
    index, length = 0, len(formula)

    def skip_quoted(position, quote):
        """Skip a quoted span starting at position; return the next index."""
        position += 1
        while position < length:
            if formula[position] == quote:
                if position + 1 < length and formula[position + 1] == quote:
                    position += 2
                    continue
                return position + 1
            position += 1
        return length

    while index < length:
        char = formula[index]
        if char == '"':
            index = skip_quoted(index, '"')
            continue
        if char == "'":
            closing = formula.find("'", index + 1)
            while closing != -1 and closing + 1 < length and formula[closing + 1] == "'":
                closing = formula.find("'", closing + 2)
            if closing == -1:
                index = length
                continue
            prefix = formula[index: closing + 1]
            if closing + 1 < length and formula[closing + 1] == "!":
                body = formula[closing + 2:]
                sub = re.match(
                    r"(\$?[A-Za-z]{1,3}\$?[0-9]+(?::\$?[A-Za-z]{1,3}\$?[0-9]+)?)", body
                )
                if sub and all(oracle_parse_a1(p) is not None for p in sub.group(1).split(":")):
                    after = body[len(sub.group(1)): len(sub.group(1)) + 1]
                    if not re.match(r"^[A-Za-z0-9_(]", after):
                        refs.append(f"{prefix}!{sub.group(1)}")
                        index = closing + 2 + len(sub.group(1))
                        continue
            index = skip_quoted(index, "'")
            continue
        cell = re.match(
            r"(\$?[A-Za-z]{1,3}\$?[0-9]+(?::\$?[A-Za-z]{1,3}\$?[0-9]+)?)", formula[index:]
        )
        if cell:
            token = cell.group(1)
            after = formula[index + len(token): index + len(token) + 1]
            preceding = formula[index - 1: index]
            valid = all(oracle_parse_a1(part) is not None for part in token.split(":"))
            if (
                valid
                and after != "!"
                and not re.match(r"^[A-Za-z0-9_(]", after)
                and not re.match(r"^[A-Za-z0-9_$]$", preceding)
            ):
                refs.append(token)
                index += len(token)
                continue
        if re.match(r"[A-Za-z_]", char):
            name = re.match(r"[A-Za-z_][A-Za-z0-9_.]*", formula[index:]).group(0)
            before_name = formula[index - 1: index]
            if (
                not re.match(r"^[A-Za-z0-9_.$]$", before_name)
                and index + len(name) < length
                and formula[index + len(name)] == "!"
            ):
                body = formula[index + len(name) + 1:]
                sub = re.match(
                    r"(\$?[A-Za-z]{1,3}\$?[0-9]+(?::\$?[A-Za-z]{1,3}\$?[0-9]+)?)", body
                )
                if sub and all(oracle_parse_a1(p) is not None for p in sub.group(1).split(":")):
                    after = body[len(sub.group(1)): len(sub.group(1)) + 1]
                    if not re.match(r"^[A-Za-z0-9_(]", after):
                        refs.append(f"{name}!{sub.group(1)}")
                        index += len(name) + 1 + len(sub.group(1))
                        continue
        index += 1
    return refs


class ColumnMathOracleTest(unittest.TestCase):
    """(a) Bijective base-26 boundaries plus 1,000 randomized round-trips."""

    def test_boundary_letters(self):
        """Exhaustive boundary table for the column alphabet."""
        expected = {
            "A": 1, "B": 2, "Z": 26, "AA": 27, "AB": 28, "AZ": 52,
            "BA": 53, "ZA": 677, "ZZ": 702, "AAA": 703, "AAB": 704,
            "AAZ": 728, "ABA": 729, "AZZ": 1378, "BAA": 1379,
            "ZZZ": 26 + 26 * 26 + 26 * 26 * 26,  # 18278: pure math beyond XFD
            "XFD": 16384,
        }
        for letters, index in expected.items():
            self.assertEqual(sheetref_module.col_letters_to_index(letters), index, letters)
            self.assertEqual(oracle_letters_to_index(letters), index, letters)
        for index in (1, 26, 27, 52, 53, 702, 703, 1379, 16384):
            self.assertEqual(
                sheetref_module.col_index_to_letters(index),
                oracle_index_to_letters(index),
            )

    def test_xfe_rejected(self):
        """XFE and beyond are outside the Excel column limit."""
        tool = SpreadsheetRefTool()
        for letters in ("XFE", "XFZ", "ZZZ"):
            result = tool.execute(mode="parse", ref=f"{letters}1")
            self.assertEqual(result["status"], "error", letters)
            self.assertIn("XFD", result["error"], letters)
        grammar = tool.execute(mode="parse", ref="AAAA1")  # four letters: not valid A1
        self.assertEqual(grammar["status"], "error")

    def test_random_round_trips(self):
        """1,000 seeded a1 -> (row, col) -> a1 round-trips vs the oracle."""
        rng = random.Random(25201)
        tool = SpreadsheetRefTool()
        for _ in range(1000):
            col = rng.randint(1, MAX_COL)
            row = rng.randint(1, MAX_ROW)
            letters = oracle_index_to_letters(col)
            self.assertEqual(oracle_letters_to_index(letters), col)
            result = tool.execute(mode="parse", ref=f"{letters}{row}")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["start"]["col"], col)
            self.assertEqual(result["start"]["row"], row)
            self.assertEqual(result["start"]["col_letters"], letters)
            self.assertEqual(result["normalized"], f"{letters}{row}")


class R1C1OracleTest(unittest.TestCase):
    """(b) R1C1 round-trips with anchors, both directions, hand-checked math."""

    HAND_TABLE = [
        # (r1c1 ref, anchor, expected A1)
        ("R[1]C[-2]", "C5", "A6"),       # row 5+1=6, col 3-2=1
        ("R[-1]C[1]", "C5", "D4"),       # row 5-1=4, col 3+1=4
        ("R[0]C[0]", "B2", "B2"),
        ("R[3]C[3]", "B2", "E5"),        # row 2+3=5, col 2+3=5
        ("R[-2]C[-1]", "D4", "C2"),      # row 4-2=2, col 4-1=3
        ("R1C1", "Z99", "$A$1"),           # absolute parts ignore the anchor
        ("R1048576C16384", "A1", "$XFD$1048576"),
        ("RC[5]", "B7", "G7"),           # bare R = anchor row
        ("R[2]C", "B7", "B9"),           # bare C = anchor column
        ("R1C[-1]", "C5", "B$1"),         # mixed absolute row, relative col
        ("R[-3]C[10]", "D10", "N7"),     # row 10-3=7, col 4+10=14
    ]

    def test_hand_relative_math(self):
        """Hand-verified R[d]C[d] resolution at known anchors."""
        tool = SpreadsheetRefTool()
        for r1c1, anchor, expected in self.HAND_TABLE:
            result = tool.execute(mode="convert", ref=r1c1, to="a1", anchor=anchor)
            self.assertEqual(result["status"], "ok", r1c1)
            self.assertTrue(result["converted"].endswith(expected), (r1c1, anchor, result["converted"]))
            if "[" in r1c1:
                self.assertIn("anchor", result["explanation"])

    def test_round_trips_both_directions(self):
        """500 seeded refs: A1 -> R1C1 -> A1 and relative R1C1 -> A1 -> R1C1."""
        rng = random.Random(25202)
        tool = SpreadsheetRefTool()
        for _ in range(500):
            row = rng.randint(2, 200)
            col = rng.randint(2, 100)
            anchor_row = rng.randint(2, 500)
            anchor_col = rng.randint(2, 500)
            anchor = f"{oracle_index_to_letters(anchor_col)}{anchor_row}"
            a1 = f"{oracle_index_to_letters(col)}{row}"
            forward = tool.execute(mode="convert", ref=a1, to="r1c1", anchor=anchor)
            self.assertEqual(forward["status"], "ok")
            self.assertEqual(forward["converted"], f"R[{row - anchor_row}]C[{col - anchor_col}]")
            back = tool.execute(mode="convert", ref=forward["converted"], to="a1", anchor=anchor)
            self.assertEqual(back["status"], "ok")
            self.assertEqual(back["converted"], a1)
            rel = f"R[{row - anchor_row}]C[{col - anchor_col}]"
            resolved = tool.execute(mode="convert", ref=rel, to="a1", anchor=anchor)
            self.assertEqual(resolved["status"], "ok")
            self.assertEqual(resolved["converted"], a1)

    def test_default_anchor_is_a1(self):
        """Documented default anchor A1 applies when no anchor is passed."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="convert", ref="R[1]C[1]", to="a1")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["converted"], "B2")
        self.assertEqual(result["anchor"], "A1")

    def test_out_of_bounds_relative(self):
        """Relative offsets that fall off the sheet are rejected."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="convert", ref="R[-5]C[1]", to="a1", anchor="B3")
        self.assertEqual(result["status"], "error")
        self.assertIn("anchor", result["error"])


class RangeCountOracleTest(unittest.TestCase):
    """(c) Exact range counts including single cells and full row/column."""

    def test_seeded_range_counts(self):
        """100 seeded ranges: size and cell_count match the oracle exactly."""
        rng = random.Random(25203)
        tool = SpreadsheetRefTool()
        cases = [("A1", "A1", 1, 1)]
        for _ in range(99):
            r1, r2 = sorted(rng.randint(1, 5000) for _ in range(2))
            c1, c2 = sorted(rng.randint(1, 2000) for _ in range(2))
            cases.append(
                (
                    f"{oracle_index_to_letters(c1)}{r1}:{oracle_index_to_letters(c2)}{r2}",
                    f"{oracle_index_to_letters(c1)}{r1}",
                    r2 - r1 + 1,
                    c2 - c1 + 1,
                )
            )
        for ref, first, rows, cols in cases:
            result = tool.execute(mode="parse", ref=ref)
            self.assertEqual(result["status"], "ok", ref)
            self.assertEqual(result["size"], {"rows": rows, "cols": cols}, ref)
            self.assertEqual(result["cell_count"], rows * cols, ref)
            self.assertEqual(result["normalized"], ref, ref)

    def test_full_row_and_column_counts(self):
        """Full row 1:1 holds 16384 cells; full column A:A reports 1,048,576."""
        tool = SpreadsheetRefTool()
        full_row = tool.execute(mode="parse", ref="1:1")
        self.assertEqual(full_row["status"], "ok")
        self.assertEqual(full_row["size"], {"rows": 1, "cols": MAX_COL})
        self.assertEqual(full_row["cell_count"], MAX_COL)
        self.assertEqual(full_row["normalized"], "1:1")
        column = tool.execute(mode="expand", ref="A:A")
        self.assertTrue(column["refused"])
        self.assertFalse(column["enumerated"])
        self.assertEqual(column["cell_count"], 1048576)
        self.assertTrue(column["full_column"])
        two_cols = tool.execute(mode="parse", ref="A:B")
        self.assertEqual(two_cols["cell_count"], 2 * MAX_ROW)


class AlgebraOracleTest(unittest.TestCase):
    """(d) Algebra vs brute-force cell sets; shift/resize hand table (30)."""

    HAND_TABLE = [
        ("shift", dict(range_a="B2:C4", op="shift", shift_rows=2, shift_cols=1), "C4:D6", 6),
        ("shift", dict(range_a="B2:C4", op="shift", shift_rows=-1, shift_cols=-1), "A1:B3", 6),
        ("shift", dict(range_a="B2:C4", op="shift", shift_rows=0, shift_cols=0), "B2:C4", 6),
        ("shift", dict(range_a="A1:B2", op="shift", shift_rows=0, shift_cols=16382), "XFC1:XFD2", 4),
        ("shift", dict(range_a="A1:A1", op="shift", shift_rows=5, shift_cols=5), "F6", 1),
        ("resize", dict(range_a="B2:C4", op="resize", resize_rows=1, resize_cols=1), "B2", 1),
        ("resize", dict(range_a="B2", op="resize", resize_rows=3, resize_cols=2), "B2:C4", 6),
        ("resize", dict(range_a="C5:E9", op="resize", resize_rows=2, resize_cols=2), "C5:D6", 4),
        ("resize", dict(range_a="B2:C4", op="resize", resize_rows=10, resize_cols=10), "B2:K11", 100),
        ("shift", dict(range_a="Sheet1!B2:C4", op="shift", shift_rows=1, shift_cols=1), "Sheet1!C3:D5", 6),
        ("resize", dict(range_a="$B$2:$C$4", op="resize", resize_rows=2, resize_cols=2), "$B$2:$C$3", 4),
        ("shift", dict(range_a="$B$2", op="shift", shift_rows=1, shift_cols=0), "$B$3", 1),
        ("resize", dict(range_a="A1", op="resize", resize_rows=1, resize_cols=16384), "1:1", 16384),  # canonical full row
        ("shift", dict(range_a="A1", op="shift", shift_rows=1048575, shift_cols=16383), "XFD1048576", 1),
        ("resize", dict(range_a="B2:C4", op="resize", resize_rows=0, resize_cols=1), "error", None),
        ("shift", dict(range_a="XFD1", op="shift", shift_cols=1), "error", None),
        ("shift", dict(range_a="A1", op="shift", shift_rows=-1), "error", None),
        ("resize", dict(range_a="XFD1", op="resize", resize_rows=1, resize_cols=2), "error", None),
        ("shift", dict(range_a="C3", op="shift", shift_rows=10, shift_cols=10), "M13", 1),
        ("shift", dict(range_a="Z9:AB12", op="shift", shift_rows=0, shift_cols=1), "AA9:AC12", 12),
        ("resize", dict(range_a="Z9:AB12", op="resize", resize_rows=4, resize_cols=3), "Z9:AB12", 12),
        ("resize", dict(range_a="A1:B2", op="resize", resize_rows=5, resize_cols=1), "A1:A5", 5),
        ("shift", dict(range_a="B2:C4", op="shift", shift_rows=3), "B5:C7", 6),
        ("shift", dict(range_a="B2:C4", op="shift", shift_cols=3), "E2:F4", 6),
        ("resize", dict(range_a="A1048575", op="resize", resize_rows=2, resize_cols=1), "A1048575:A1048576", 2),
        ("shift", dict(range_a="A1048576", op="shift", shift_rows=1), "error", None),
        ("resize", dict(range_a="C5", op="resize", resize_rows=1048576, resize_cols=1), "error", None),
        ("shift", dict(range_a="'My Sheet'!B2", op="shift", shift_rows=1, shift_cols=1), "'My Sheet'!C3", 1),
        ("resize", dict(range_a="B2:C4", op="resize", resize_rows=2, resize_cols=3), "B2:D3", 6),
        ("shift", dict(range_a="A1:B2", op="shift", shift_rows=1048575), "error", None),
    ]

    def test_hand_table(self):
        """30 hand-computed shift/resize expectations."""
        tool = SpreadsheetRefTool()
        self.assertEqual(len(self.HAND_TABLE), 30)
        for _, kwargs, expected, count in self.HAND_TABLE:
            result = tool.execute(mode="algebra", **kwargs)
            if expected == "error":
                self.assertEqual(result["status"], "error", kwargs)
            else:
                self.assertEqual(result["status"], "ok", kwargs)
                self.assertEqual(result["result"], expected, kwargs)
                if count is not None:
                    self.assertEqual(result["cell_count"], count, kwargs)

    @staticmethod
    def _rand_range(rng):
        r1 = rng.randint(1, 10)
        r2 = r1 + rng.randint(0, 6)
        c1 = rng.randint(1, 10)
        c2 = c1 + rng.randint(0, 6)
        return f"{oracle_index_to_letters(c1)}{r1}:{oracle_index_to_letters(c2)}{r2}"

    def test_set_operations_vs_brute_force(self):
        """300 seeded pairs: intersection/union/subtract match cell-set math."""
        rng = random.Random(25204)
        tool = SpreadsheetRefTool()
        for trial in range(300):
            a, b = self._rand_range(rng), self._rand_range(rng)
            set_a, set_b = oracle_cells_of(a), oracle_cells_of(b)
            expected = {
                "intersection": set_a & set_b,
                "union": set_a | set_b,
                "subtract": set_a - set_b,
            }
            for op, want in expected.items():
                result = tool.execute(mode="algebra", range_a=a, range_b=b, op=op)
                self.assertEqual(result["status"], "ok", (trial, op, a, b))
                self.assertEqual(result["cell_count"], len(want), (op, a, b))
                got = set()
                for area in result["areas"]:
                    got |= oracle_cells_of(area)
                self.assertEqual(got, want, (op, a, b, result["areas"]))
                if result["result"] is not None:
                    self.assertEqual(oracle_cells_of(result["result"]), want, (op, a, b))

    def test_intersection_space_operator_example(self):
        """Spec example: A1:B3 intersected with B2:C4 -> B2:B3."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="algebra", range_a="A1:B3", range_b="B2:C4", op="intersection")
        self.assertEqual(result["result"], "B2:B3")
        self.assertEqual(result["cell_count"], 2)

    def test_union_bounding_box_and_multi_area(self):
        """Contiguous unions collapse to a bounding box; others go multi-area."""
        tool = SpreadsheetRefTool()
        box = tool.execute(mode="algebra", range_a="A1:B2", range_b="C1:D2", op="union")
        self.assertEqual(box["result"], "A1:D2")
        self.assertTrue(box["contiguous"])
        multi = tool.execute(mode="algebra", range_a="A1:A3", range_b="C1:C3", op="union")
        self.assertIsNone(multi["result"])
        self.assertFalse(multi["contiguous"])
        self.assertEqual(multi["cell_count"], 6)
        got = set()
        for area in multi["areas"]:
            got |= oracle_cells_of(area)
        self.assertEqual(got, oracle_cells_of("A1:A3") | oracle_cells_of("C1:C3"))

    def test_subtract_example(self):
        """Spec example: A1:C3 minus B2 -> 8 cells across areas."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="algebra", range_a="A1:C3", range_b="B2:B2", op="subtract")
        self.assertEqual(result["cell_count"], 8)
        got = set()
        for area in result["areas"]:
            got |= oracle_cells_of(area)
        self.assertEqual(got, oracle_cells_of("A1:C3") - {(2, 2)})

    def test_same_sheet_required(self):
        """Cross-sheet algebra is refused."""
        tool = SpreadsheetRefTool()
        result = tool.execute(
            mode="algebra", range_a="Sheet1!A1:B2", range_b="Sheet2!B2:C3", op="intersection"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("same sheet", result["error"])


class ParseSemanticsTest(unittest.TestCase):
    """parse mode structure: sheets, $ semantics, normalization, errors."""

    def test_parse_basics(self):
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="parse", ref="$B$2")
        self.assertEqual(result["kind"], "cell")
        self.assertIsNone(result["sheet"])
        self.assertTrue(result["start"]["abs_col"])
        self.assertTrue(result["start"]["abs_row"])
        self.assertEqual(result["normalized"], "$B$2")
        self.assertEqual(result["size"], {"rows": 1, "cols": 1})
        mixed = tool.execute(mode="parse", ref="B$2")
        self.assertFalse(mixed["start"]["abs_col"])
        self.assertTrue(mixed["start"]["abs_row"])
        relative = tool.execute(mode="parse", ref="Sheet1!A1:B2")
        self.assertEqual(relative["sheet"], "Sheet1")
        self.assertEqual(relative["size"], {"rows": 2, "cols": 2})
        self.assertEqual(relative["cell_count"], 4)

    def test_sheet_forms(self):
        tool = SpreadsheetRefTool()
        plain = tool.execute(mode="parse", ref="Sheet1!A1:B2")
        self.assertEqual(plain["sheet"], "Sheet1")
        self.assertEqual(plain["normalized"], "Sheet1!A1:B2")
        quoted = tool.execute(mode="parse", ref="'My Sheet'!A1")
        self.assertEqual(quoted["sheet"], "My Sheet")
        self.assertTrue(quoted["sheet_quoted"])
        self.assertEqual(quoted["normalized"], "'My Sheet'!A1")
        escaped = tool.execute(mode="parse", ref="'It''s'!A1")
        self.assertEqual(escaped["sheet"], "It's")
        unquoted_space = tool.execute(mode="parse", ref="My Sheet!A1")
        self.assertEqual(unquoted_space["status"], "error")

    def test_reordering_and_notes(self):
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="parse", ref="B2:A1")
        self.assertEqual(result["normalized"], "A1:B2")
        self.assertTrue(any("re-ordered" in note for note in result["notes"]))
        self.assertEqual(tool.execute(mode="parse", ref="A5:A1")["normalized"], "A1:A5")

    def test_errors_carry_positions(self):
        tool = SpreadsheetRefTool()
        beyond_col = tool.execute(mode="parse", ref="B1:XFE5")
        self.assertEqual(beyond_col["status"], "error")
        self.assertEqual(beyond_col["position"], 3)  # XFE starts after 'B1:'
        beyond_row = tool.execute(mode="parse", ref="A1048577")
        self.assertEqual(beyond_row["status"], "error")
        self.assertIn("1048576", beyond_row["error"])
        middle_dollar = tool.execute(mode="parse", ref="A$B$1")
        self.assertEqual(middle_dollar["status"], "error")
        empty = tool.execute(mode="parse", ref="")
        self.assertEqual(empty["status"], "error")
        extra_colon = tool.execute(mode="parse", ref="A1:B2:C3")
        self.assertEqual(extra_colon["status"], "error")
        self.assertEqual(extra_colon["position"], 5)  # second ':'

    def test_r1c1_mixed_forms_parse(self):
        tool = SpreadsheetRefTool()
        absolute = tool.execute(mode="parse", ref="R2C3")
        self.assertEqual(absolute["start"]["row"], 2)
        self.assertEqual(absolute["start"]["col"], 3)
        self.assertEqual(absolute["start"]["a1"], "$C$2")
        off_sheet = tool.execute(mode="parse", ref="R2C[-1]")  # col 0 at anchor A1
        self.assertEqual(off_sheet["status"], "error")
        ok = tool.execute(mode="parse", ref="R[1]C[1]")  # default anchor A1
        self.assertEqual(ok["normalized"], "B2")
        mixed_style = tool.execute(mode="parse", ref="R2C[1]")  # default anchor A1
        self.assertEqual(mixed_style["normalized"], "B$2")


class ExpandModeTest(unittest.TestCase):
    """(f, part 1) expansion cap behavior."""

    def test_small_expansion(self):
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="expand", ref="A1:B2")
        self.assertTrue(result["enumerated"])
        self.assertEqual(result["cells"], ["A1", "B1", "A2", "B2"])
        self.assertEqual(result["order"], "row-major")

    def test_cap_boundary(self):
        """Exactly max_expand_cells enumerates; one more cell refuses."""
        tool = SpreadsheetRefTool()
        exact = tool.execute(mode="expand", ref="A1:CV100")  # 100 cols x 100 rows
        self.assertEqual(exact["cell_count"], 10000)
        self.assertTrue(exact["enumerated"])
        self.assertEqual(len(exact["cells"]), 10000)
        over = tool.execute(mode="expand", ref="A1:CW100")  # 101 columns
        self.assertEqual(over["cell_count"], 10100)
        self.assertFalse(over["enumerated"])
        self.assertTrue(over["refused"])
        self.assertNotIn("cells", over)

    def test_single_cell_and_sheet_prefix(self):
        tool = SpreadsheetRefTool()
        single = tool.execute(mode="expand", ref="C3")
        self.assertEqual(single["cells"], ["C3"])
        prefixed = tool.execute(mode="expand", ref="Sheet9!A1:B1")
        self.assertEqual(prefixed["cells"], ["Sheet9!A1", "Sheet9!B1"])


class ExtractRefsOracleTest(unittest.TestCase):
    """(e) extract_refs vs an independent tokenizer, 200 seeded formulas."""

    def test_spec_examples(self):
        tool = SpreadsheetRefTool()
        by_ref = lambda result: {entry["ref"] for entry in result["refs"]}
        result = tool.execute(mode="extract_refs", formula="=SUM(A1:A10)")
        self.assertEqual(by_ref(result), {"A1:A10"})
        result = tool.execute(mode="extract_refs", formula="=$B$2*C3")
        self.assertEqual(by_ref(result), {"$B$2", "C3"})
        self.assertEqual(result["refs"][0]["addressing"], "absolute")
        self.assertEqual(result["refs"][1]["addressing"], "relative")
        result = tool.execute(mode="extract_refs", formula="=Sheet2!C3+1")
        self.assertEqual(by_ref(result), {"Sheet2!C3"})
        self.assertTrue(result["refs"][0]["cross_sheet"])
        result = tool.execute(mode="extract_refs", formula="='Q3 Data'!A1:B2")
        self.assertEqual(by_ref(result), {"'Q3 Data'!A1:B2"})
        self.assertEqual(result["refs"][0]["sheet"], "Q3 Data")
        result = tool.execute(mode="extract_refs", formula='=IF(A1>0,"text with A1 inside",B1)')
        self.assertEqual(by_ref(result), {"A1", "B1"})
        self.assertEqual(result["quoted_strings"], 1)
        result = tool.execute(mode="extract_refs", formula="=IF(A1>0,B1,C1)")
        self.assertEqual(by_ref(result), {"A1", "B1", "C1"})
        result = tool.execute(mode="extract_refs", formula="=TaxRate*A1")
        self.assertIn("TaxRate", result["defined_name_candidates"])

    def test_seeded_formulas_vs_oracle(self):
        """200 seeded formulas agree with the independent tokenizer."""
        rng = random.Random(25205)
        tool = SpreadsheetRefTool()
        fragments = [
            "A1", "$B$2", "C$3", "$D4", "E5:F9", "Sheet2!C3", "'Q3 Data'!A1:B2",
            "SUM(", "IF(", ")", ",", ">", "*", "+", "TaxRate", '"text A1 here"',
            '""quoted""', "0", "100", "LOG10(", "XFE1", "MAX(", "G7:H8",
        ]
        for trial in range(200):
            formula = "=" + "".join(rng.choice(fragments) for _ in range(rng.randint(3, 12)))
            result = tool.execute(mode="extract_refs", formula=formula)
            self.assertEqual(result["status"], "ok", formula)
            expected = set(oracle_formula_refs(formula))
            got = {entry["ref"] for entry in result["refs"]}
            self.assertEqual(got, expected, (formula, got, expected))

    def test_addressing_and_size_classification(self):
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="extract_refs", formula="=SUM($B$2:$B$9)+C3")
        entries = {entry["ref"]: entry for entry in result["refs"]}
        self.assertEqual(entries["$B$2:$B$9"]["addressing"], "absolute")
        self.assertEqual(entries["$B$2:$B$9"]["size"], {"rows": 8, "cols": 1})
        self.assertEqual(entries["C3"]["addressing"], "relative")
        self.assertEqual(entries["C3"]["kind"], "cell")


class PathologicalInputTest(unittest.TestCase):
    """(f) caps: expansion refusal, ~10k-char formulas, long inputs."""

    def test_ten_thousand_char_formula(self):
        tool = SpreadsheetRefTool()
        formula = "=SUM(" + ",".join(f"A{row}" for row in range(1, 1800)) + ")"
        self.assertGreater(len(formula), 9000)
        self.assertLess(len(formula), tool.max_input_length)
        result = tool.execute(mode="extract_refs", formula=formula)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["ref_count"], 1799)
        self.assertEqual(len({entry["ref"] for entry in result["refs"]}), 1799)

    def test_input_length_cap(self):
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="extract_refs", formula="=" + "A1+" * 6000)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_length", result["error"])
        result = tool.execute(mode="parse", ref="A" * 6000)
        self.assertEqual(result["status"], "error")

    def test_huge_algebra_counts_stay_arithmetic(self):
        """Full-sheet algebra counts never enumerate cells."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="algebra", range_a="A:A", range_b="B:B", op="union")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["cell_count"], 2 * MAX_ROW)
        self.assertTrue(result["contiguous"])
        self.assertEqual(result["result"], "A:B")
        split = tool.execute(mode="algebra", range_a="A:A", range_b="C:C", op="union")
        self.assertEqual(split["cell_count"], 2 * MAX_ROW)
        self.assertFalse(split["contiguous"])
        self.assertEqual(split["areas"], [])  # decomposition skipped above the cap
        intersection = tool.execute(mode="algebra", range_a="A:A", range_b="1:1", op="intersection")
        self.assertEqual(intersection["result"], "A1")
        subtraction = tool.execute(mode="algebra", range_a="A:A", range_b="A1:A2", op="subtract")
        self.assertEqual(subtraction["cell_count"], MAX_ROW - 2)

    def test_determinism(self):
        """Repeated calls return identical payloads."""
        tool = SpreadsheetRefTool()
        first = tool.execute(mode="extract_refs", formula="=SUM(A1:A10)+TaxRate*'Q 3'!B2:C4")
        for _ in range(5):
            again = tool.execute(mode="extract_refs", formula="=SUM(A1:A10)+TaxRate*'Q 3'!B2:C4")
            self.assertEqual(again, first)

    def test_no_secret_material_in_output(self):
        """Tool output never embeds credential-like literals."""
        tool = SpreadsheetRefTool()
        result = tool.execute(mode="parse", ref="A1:B2")
        self.assertNotIn("ghp_", repr(result))
        self.assertNotIn("token", repr(result))


class SpreadsheetRefRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped spreadsheet_ref_tool.yaml."""

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
        """Verify the shipped yaml resolves to a tool component exposing SpreadsheetRefTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "SpreadsheetRefTool")

    def test_manager(self):
        """Verify the SpreadsheetRefTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, SpreadsheetRefTool)
        self.assertEqual(tool.input_keys, ["mode", "ref"])


if __name__ == "__main__":
    unittest.main()
