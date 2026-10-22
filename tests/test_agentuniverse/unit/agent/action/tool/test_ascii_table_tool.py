#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_ascii_table_tool.py

"""Offline unit tests for AsciiTableTool.

The tool is built purely on the standard library (csv, io,
unicodedata) and never touches the network, so this suite runs fully
offline. Every rendered table is asserted against an exact
ground-truth string written out by hand: each style (markdown, ascii,
grid, simple), CJK alignment, header variants, the alignment matrix,
truncation, transposition and delimited parsing (including quoted
fields) all have byte-exact expected outputs. Error behaviour is
covered by a matrix of ValueError cases plus one structured
content-level error payload.
"""

import unicodedata
import unittest

from agentuniverse.agent.action.tool.common_tool import AsciiTableTool
from agentuniverse.agent.action.tool.common_tool.ascii_table_tool import (
    AsciiTableTool as DirectAsciiTableTool,
)

# --------------------------------------------------------------------- #
# Shared fixtures
# --------------------------------------------------------------------- #
PEOPLE_HEADER = ["Name", "Age"]
PEOPLE_ROWS = [["Alice", "30"], ["Bob", "25"]]
# Column widths: Name -> max(4, 5, 3) = 5, Age -> max(3, 2, 2) = 3.
MARKDOWN_PEOPLE = "\n".join(
    [
        "| Name  | Age |",
        "|-------|-----|",
        "| Alice | 30  |",
        "| Bob   | 25  |",
    ]
)
ASCII_PEOPLE = "\n".join(
    [
        "+-------+-----+",
        "| Name  | Age |",
        "+-------+-----+",
        "| Alice | 30  |",
        "| Bob   | 25  |",
        "+-------+-----+",
    ]
)
GRID_PEOPLE = "\n".join(
    [
        "+-------+-----+",
        "| Name  | Age |",
        "+-------+-----+",
        "| Alice | 30  |",
        "+-------+-----+",
        "| Bob   | 25  |",
        "+-------+-----+",
    ]
)
SIMPLE_PEOPLE = "\n".join(
    [
        "Name   Age",
        "-----  ---",
        "Alice  30 ",
        "Bob    25 ",
    ]
)

CJK_HEADER = ["名字", "値"]
CJK_ROWS = [["日本語", "1"], ["x", "22"]]
# Display widths (east-asian W/F characters count as two columns):
# column 1 -> max(4, 6, 1) = 6, column 2 -> max(2, 1, 2) = 2.
MARKDOWN_CJK = "\n".join(
    [
        "| 名字   | 値 |",
        "|--------|----|",
        "| 日本語 | 1  |",
        "| x      | 22 |",
    ]
)


def _display_width(text: str) -> int:
    """Independent re-implementation of the expected width rule."""
    return sum(
        2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        for char in text
    )


class AsciiTableToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib AsciiTableTool."""

    def setUp(self) -> None:
        self.tool = AsciiTableTool()

    # ------------------------------------------------------------------ #
    # render mode — styles
    # ------------------------------------------------------------------ #

    def test_markdown_is_default_style(self) -> None:
        result = self.tool.execute(rows=PEOPLE_ROWS, header=PEOPLE_HEADER, mode="render")
        self.assertEqual(
            result,
            {
                "mode": "render",
                "style": "markdown",
                "header": True,
                "rows": 2,
                "columns": 2,
                "result": MARKDOWN_PEOPLE,
            },
        )

    def test_markdown_explicit_style_matches_default(self) -> None:
        result = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="markdown"
        )
        self.assertEqual(result["result"], MARKDOWN_PEOPLE)

    def test_ascii_style_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="ascii"
        )
        self.assertEqual(result["style"], "ascii")
        self.assertEqual(result["result"], ASCII_PEOPLE)

    def test_grid_style_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="grid"
        )
        self.assertEqual(result["style"], "grid")
        self.assertEqual(result["result"], GRID_PEOPLE)

    def test_simple_style_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="simple"
        )
        self.assertEqual(result["style"], "simple")
        self.assertEqual(result["result"], SIMPLE_PEOPLE)

    def test_markdown_without_header_exact(self) -> None:
        # Widths: column 1 -> max(0, 1, 3) = 3, column 2 -> max(0, 2, 1) = 2.
        result = self.tool.execute(
            mode="render", rows=[["a", "bb"], ["ccc", "d"]], style="markdown"
        )
        self.assertEqual(result["header"], False)
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "|     |    |",
                    "|-----|----|",
                    "| a   | bb |",
                    "| ccc | d  |",
                ]
            ),
        )

    def test_grid_without_header_exact(self) -> None:
        result = self.tool.execute(mode="render", rows=[["a"], ["bb"]], style="grid")
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "+----+",
                    "| a  |",
                    "+----+",
                    "| bb |",
                    "+----+",
                ]
            ),
        )

    def test_ascii_single_cell_exact(self) -> None:
        result = self.tool.execute(mode="render", rows=[["only"]], style="ascii")
        self.assertEqual(
            result["result"],
            "\n".join(["+------+", "| only |", "+------+"]),
        )

    def test_simple_without_header_has_no_underline(self) -> None:
        result = self.tool.execute(mode="render", rows=[["a", "b"]], style="simple")
        self.assertEqual(result["result"], "a  b")

    # ------------------------------------------------------------------ #
    # render mode — CJK east-asian width awareness
    # ------------------------------------------------------------------ #

    def test_markdown_cjk_alignment_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=CJK_ROWS, header=CJK_HEADER, style="markdown"
        )
        self.assertEqual(result["result"], MARKDOWN_CJK)

    def test_ascii_cjk_alignment_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=CJK_ROWS, header=CJK_HEADER, style="ascii"
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "+--------+----+",
                    "| 名字   | 値 |",
                    "+--------+----+",
                    "| 日本語 | 1  |",
                    "| x      | 22 |",
                    "+--------+----+",
                ]
            ),
        )

    def test_cjk_columns_line_up_in_display_width(self) -> None:
        # Invariant checked independently of the exact strings: in every
        # bordered line the boundary characters ('|' for cell rows, '+'
        # for border rows) must sit at the same display columns even
        # when cells contain wide characters.
        for style in ("markdown", "ascii", "grid"):
            with self.subTest(style=style):
                table = self.tool.execute(
                    mode="render", rows=CJK_ROWS, header=CJK_HEADER, style=style
                )["result"]
                boundaries = []
                for line in table.split("\n"):
                    columns = []
                    width = 0
                    for char in line:
                        if char in ("|", "+"):
                            columns.append(width)
                        width += _display_width(char)
                    boundaries.append(tuple(columns))
                self.assertEqual(len(set(boundaries)), 1)

    # ------------------------------------------------------------------ #
    # render mode — alignment matrix
    # ------------------------------------------------------------------ #

    def test_align_left_explicit_markdown_exact(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=PEOPLE_ROWS,
            header=PEOPLE_HEADER,
            style="markdown",
            align="left",
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "| Name  | Age |",
                    "|:------|:----|",
                    "| Alice | 30  |",
                    "| Bob   | 25  |",
                ]
            ),
        )

    def test_align_center_markdown_exact(self) -> None:
        # Widths: column 1 -> max(1, 3) = 3, column 2 -> max(2, 1) = 2.
        result = self.tool.execute(
            mode="render",
            rows=[["ccc", "d"]],
            header=["a", "bb"],
            style="markdown",
            align="center",
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "|  a  | bb |",
                    "|:---:|:--:|",
                    "| ccc | d  |",
                ]
            ),
        )

    def test_align_right_markdown_exact(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=[["ccc", "d"]],
            header=["a", "bb"],
            style="markdown",
            align="right",
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "|   a | bb |",
                    "|----:|---:|",
                    "| ccc |  d |",
                ]
            ),
        )

    def test_align_per_column_list_exact(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=[["ccc", "d"]],
            header=["a", "bb"],
            style="markdown",
            align=["left", "right"],
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "| a   | bb |",
                    "|:----|---:|",
                    "| ccc |  d |",
                ]
            ),
        )

    def test_align_center_extra_space_goes_right(self) -> None:
        # "x" in a width-2 column: one pad space, floor(1/2) on the left
        # means zero left spaces, so the extra space lands on the right.
        result = self.tool.execute(
            mode="render", rows=[["dd"]], header=["x"], style="ascii", align="center"
        )
        self.assertEqual(
            result["result"],
            "\n".join(["+----+", "| x  |", "+----+", "| dd |", "+----+"]),
        )

    def test_align_center_wide_padding_exact(self) -> None:
        # "a" in a width-4 column: pad 2 -> one space each side inside
        # the field, plus the one-space cell margins of the box.
        result = self.tool.execute(
            mode="render", rows=[["abcd"]], header=["a"], style="ascii", align="center"
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                ["+------+", "|  a   |", "+------+", "| abcd |", "+------+"]
            ),
        )

    # ------------------------------------------------------------------ #
    # render mode — truncation (max_col_width)
    # ------------------------------------------------------------------ #

    def test_truncation_ascii_right_aligned_exact(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=[["abcdefghij", "x"]],
            header=["col", "y"],
            style="simple",
            align="right",
            max_col_width=5,
        )
        self.assertEqual(
            result["result"],
            "\n".join(["  col  y", "-----  -", "abcd…  x"]),
        )

    def test_truncation_cjk_exact(self) -> None:
        # "日本語ですよ" has display width 12 > 5, so it is cut to a
        # display width of 4 ("日本") plus the one-column ellipsis.
        result = self.tool.execute(
            mode="render",
            rows=[["日本語ですよ", "end"]],
            header=["項目", "x"],
            style="simple",
            max_col_width=5,
        )
        self.assertEqual(
            result["result"],
            "\n".join(["項目   x  ", "-----  ---", "日本…  end"]),
        )

    def test_truncation_leaves_short_cells_untouched(self) -> None:
        result = self.tool.execute(
            mode="render", rows=[["ab", "c"]], max_col_width=10, style="grid"
        )
        self.assertEqual(
            result["result"],
            "\n".join(["+----+---+", "| ab | c |", "+----+---+"]),
        )

    def test_truncation_limit_one_renders_bare_ellipsis(self) -> None:
        result = self.tool.execute(
            mode="render", rows=[["abcdef"]], max_col_width=1, style="simple"
        )
        self.assertEqual(result["result"], "…")

    def test_truncation_applies_to_header_too(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=[["data"]],
            header=["truncated-header"],
            max_col_width=4,
            style="simple",
        )
        self.assertEqual(result["result"], "\n".join(["tru…", "----", "data"]))

    # ------------------------------------------------------------------ #
    # render mode — cell coercion and ragged policy
    # ------------------------------------------------------------------ #

    def test_cell_coercion_scalars_exact(self) -> None:
        result = self.tool.execute(
            mode="render",
            rows=[[1, True, None, 2.5]],
            header=["id", "ok", "note", "ratio"],
            style="markdown",
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "| id | ok   | note | ratio |",
                    "|----|------|------|-------|",
                    "| 1  | True |      | 2.5   |",
                ]
            ),
        )

    def test_ragged_rows_rejected_by_default(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="render", rows=[["a"], ["b", "c"]], header=["h1"]
            )
        self.assertIn("ragged='pad'", str(ctx.exception))

    def test_ragged_rows_padded_exact(self) -> None:
        result = self.tool.execute(
            mode="render", rows=[["a", "b"]], header=["A"], ragged="pad"
        )
        self.assertEqual(
            result["result"],
            "\n".join(["| A |   |", "|---|---|", "| a | b |"]),
        )

    # ------------------------------------------------------------------ #
    # transpose mode
    # ------------------------------------------------------------------ #

    def test_transpose_simple_exact(self) -> None:
        result = self.tool.execute(
            mode="transpose",
            rows=PEOPLE_ROWS,
            header=PEOPLE_HEADER,
            style="simple",
        )
        self.assertEqual(
            result,
            {
                "mode": "transpose",
                "style": "simple",
                "header": False,
                "rows": 2,
                "columns": 3,
                "result": "\n".join(["Name  Alice  Bob", "Age   30     25 "]),
            },
        )

    def test_transpose_without_header_exact(self) -> None:
        result = self.tool.execute(
            mode="transpose", rows=[["a", "b"], ["c", "d"]], style="simple"
        )
        self.assertEqual(result["result"], "\n".join(["a  c", "b  d"]))

    def test_transpose_single_row_becomes_single_column(self) -> None:
        result = self.tool.execute(
            mode="transpose", rows=[["a", "bb", "c"]], style="ascii"
        )
        self.assertEqual(result["columns"], 1)
        self.assertEqual(
            result["result"],
            "\n".join(
                ["+----+", "| a  |", "| bb |", "| c  |", "+----+"]
            ),
        )

    def test_transpose_ragged_rejected_not_silently_truncated(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="transpose", rows=[["a", "b"], ["c"]])

    def test_transpose_ragged_padded_exact(self) -> None:
        result = self.tool.execute(
            mode="transpose", rows=[["a", "b"]], header=["h1"], ragged="pad", style="simple"
        )
        self.assertEqual(
            result["result"],
            "\n".join(["h1  a", "    b"]),
        )

    # ------------------------------------------------------------------ #
    # from_csv / from_tsv modes
    # ------------------------------------------------------------------ #

    def test_from_csv_basic_markdown_exact(self) -> None:
        result = self.tool.execute(
            mode="from_csv", text="Name,Age\nAlice,30\nBob,25"
        )
        self.assertEqual(
            result,
            {
                "mode": "from_csv",
                "style": "markdown",
                "header": True,
                "rows": 2,
                "columns": 2,
                "result": MARKDOWN_PEOPLE,
                "delimiter": ",",
            },
        )

    def test_from_csv_quoted_fields_with_commas_exact(self) -> None:
        result = self.tool.execute(
            mode="from_csv", text='"Last, First",Age\n"Doe, John",42'
        )
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "| Last, First | Age |",
                    "|-------------|-----|",
                    "| Doe, John   | 42  |",
                ]
            ),
        )

    def test_from_csv_escaped_quotes_exact(self) -> None:
        result = self.tool.execute(mode="from_csv", text='"say ""hi""",x\n1,2')
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    '| say "hi" | x |',
                    "|----------|---|",
                    "| 1        | 2 |",
                ]
            ),
        )

    def test_from_tsv_basic_exact(self) -> None:
        result = self.tool.execute(mode="from_tsv", text="a\tb\n1\t2")
        self.assertEqual(result["delimiter"], "\t")
        self.assertEqual(
            result["result"],
            "\n".join(["| a | b |", "|---|---|", "| 1 | 2 |"]),
        )

    def test_from_csv_custom_delimiter_exact(self) -> None:
        result = self.tool.execute(
            mode="from_csv", text="a;b\n1;2", delimiter=";"
        )
        self.assertEqual(result["delimiter"], ";")
        self.assertEqual(
            result["result"],
            "\n".join(["| a | b |", "|---|---|", "| 1 | 2 |"]),
        )

    def test_from_csv_has_header_false_exact(self) -> None:
        result = self.tool.execute(
            mode="from_csv", text="a,b\n1,2", has_header=False
        )
        self.assertEqual(result["header"], False)
        self.assertEqual(
            result["result"],
            "\n".join(["|   |   |", "|---|---|", "| a | b |", "| 1 | 2 |"]),
        )

    def test_from_tsv_crlf_line_endings_exact(self) -> None:
        result = self.tool.execute(mode="from_tsv", text="a\tb\r\n1\t2\r\n")
        self.assertEqual(
            result["result"],
            "\n".join(["| a | b |", "|---|---|", "| 1 | 2 |"]),
        )

    def test_from_csv_blank_lines_skipped(self) -> None:
        result = self.tool.execute(mode="from_csv", text="a,b\n\n1,2\n")
        self.assertEqual(result["rows"], 1)
        self.assertEqual(
            result["result"],
            "\n".join(["| a | b |", "|---|---|", "| 1 | 2 |"]),
        )

    def test_from_csv_styles_and_options_pass_through(self) -> None:
        result = self.tool.execute(
            mode="from_csv",
            text="x,y\nlong-value,1",
            style="simple",
            align="right",
            max_col_width=6,
        )
        self.assertEqual(
            result["result"],
            "\n".join(["     x  y", "------  -", "long-…  1"]),
        )

    def test_from_csv_strict_quoting_error_payload(self) -> None:
        result = self.tool.execute(mode="from_csv", text='"a"x,b\n1,2')
        self.assertEqual(result["mode"], "from_csv")
        self.assertEqual(result["error"]["type"], "invalid_delimited_text")
        self.assertIn("quoting", result["error"]["message"])

    def test_from_tsv_quoted_tab_cell_rejected(self) -> None:
        # A quoted field protects the delimiter from splitting, but the
        # resulting cell then contains a tab, which single-line table
        # rendering cannot represent — rejected strictly.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="from_tsv", text='"a\tb"\tc\n1\t2')

    def test_from_csv_header_only_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="from_csv", text="a,b")

    def test_from_csv_whitespace_only_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="from_csv", text="a,b\n\n\n")

    def test_delimited_cell_with_newline_rejected(self) -> None:
        # A quoted field may span lines in CSV, but single-line table
        # rendering cannot represent it, so it is rejected strictly.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="from_csv", text='a,b\n"line1\nline2",x')

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_deterministic_output(self) -> None:
        first = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="grid"
        )
        second = self.tool.execute(
            mode="render", rows=PEOPLE_ROWS, header=PEOPLE_HEADER, style="grid"
        )
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="draw", rows=[["a"]])
        self.assert_invalid(mode=None, rows=[["a"]])
        self.assert_invalid(mode=123, rows=[["a"]])

    def test_invalid_style(self) -> None:
        self.assert_invalid(mode="render", rows=[["a"]], style="fancy")
        self.assert_invalid(mode="render", rows=[["a"]], style="html")

    def test_invalid_align(self) -> None:
        self.assert_invalid(mode="render", rows=[["a"]], align="middle")
        self.assert_invalid(mode="render", rows=[["a"]], align=["left", "up"])
        self.assert_invalid(mode="render", rows=[["a"]], align=5)
        self.assert_invalid(mode="render", rows=[["a"]], align=[])
        # Per-column list must match the column count.
        self.assert_invalid(mode="render", rows=[["a"]], align=["left", "right"])
        self.assert_invalid(mode="render", rows=[["a", "b"]], align=["left"])

    def test_invalid_max_col_width(self) -> None:
        for bad in (0, -1, "5", True, 2.5):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="render", rows=[["a"]], max_col_width=bad)

    def test_invalid_ragged(self) -> None:
        self.assert_invalid(mode="render", rows=[["a"]], ragged="ignore")
        self.assert_invalid(mode="render", rows=[["a"]], ragged=1)

    def test_invalid_rows_container(self) -> None:
        for bad in (None, "a;b", 42, {"a": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="render", rows=bad)

    def test_invalid_row_items(self) -> None:
        self.assert_invalid(mode="render", rows=[["a"], "b"])
        self.assert_invalid(mode="render", rows=[["a"], 5])
        self.assert_invalid(mode="render", rows=[None])

    def test_invalid_cell_types(self) -> None:
        for bad in ({"a": 1}, [1], b"x"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="render", rows=[[bad]])

    def test_invalid_cell_control_characters(self) -> None:
        for bad in ("a\nb", "a\rb", "a\tb"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="render", rows=[[bad]])

    def test_invalid_header(self) -> None:
        self.assert_invalid(mode="render", rows=[["a"]], header="Name")
        self.assert_invalid(mode="render", rows=[["a"]], header=[])
        self.assert_invalid(mode="render", rows=[["a"]], header=[{"a": 1}])
        self.assert_invalid(mode="render", rows=[["a"]], header=["a\nb"])

    def test_empty_table_rejected(self) -> None:
        self.assert_invalid(mode="render", rows=[])
        self.assert_invalid(mode="render", rows=[[]])
        self.assert_invalid(mode="transpose", rows=[[]])

    def test_invalid_text_for_delimited_modes(self) -> None:
        for bad in (None, 123, True, b"a,b"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="from_csv", text=bad)

    def test_empty_text_rejected_for_delimited_modes(self) -> None:
        self.assert_invalid(mode="from_csv", text="")
        self.assert_invalid(mode="from_tsv", text="")

    def test_invalid_delimiter(self) -> None:
        for bad in ("", ";;", 5, '"'):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="from_csv", text="a,b\nc,d", delimiter=bad)

    def test_invalid_has_header(self) -> None:
        self.assert_invalid(mode="from_csv", text="a,b\nc,d", has_header="yes")
        self.assert_invalid(mode="from_csv", text="a,b\nc,d", has_header=1)

    def test_size_limits(self) -> None:
        # Row limit.
        self.assert_invalid(mode="render", rows=[["x"]] * 10_001)
        # Cell character limit.
        self.assert_invalid(mode="render", rows=[["a" * 10_001]])
        # Input text limit for the delimited modes.
        self.assert_invalid(mode="from_csv", text="a\n" * 60_000)
        # Values inside the limits still succeed.
        ok = self.tool.execute(mode="render", rows=[["x"]] * 10_000)
        self.assertEqual(ok["rows"], 10_000)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectAsciiTableTool, AsciiTableTool)
        self.assertEqual(self.tool.name, "ascii_table_tool")
        self.assertIn("render", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("AsciiTableTool", __all__)


if __name__ == "__main__":
    unittest.main()
