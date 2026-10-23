#!/usr/bin/env python3
"""Offline unit tests for AsciiTableTool.

Oracle: the wcwidth package (test-only, skipped when absent) pins the
display-width model over a wide corpus; every rendered table satisfies
the per-line width invariant (all lines of a table have one display
width, modulo the separator rows which have their own consistent width);
markdown output round-trips through the csv module.
"""

import csv
import io
import unittest

from agentuniverse.agent.action.tool.common_tool.ascii_table_tool import (
    AsciiTableTool,
    display_width,
)

try:
    import wcwidth

    _HAS_WCWIDTH = True
except Exception:  # pragma: no cover
    _HAS_WCWIDTH = False

CORPUS = [
    "hello", "名称与值", "café naïve", "café naïve",  # precomposed + decomposed
    "a​b", "─│┌┐└┘",  # ZWSP, box chars
    "①②③", "±÷", "Ω≈ç√∫", " -space", "tab\tinside",
    "ＡＢＣ", "ﾊﾝｶｸ", "×÷≠", "1½", "é",
]


class MeasureTest(unittest.TestCase):
    def setUp(self):
        self.tool = AsciiTableTool()

    def test_zero_width(self):
        self.assertEqual(display_width("é"), 1)  # e + combining acute
        self.assertEqual(display_width("a​b"), 2)  # ZWSP is zero
        self.assertEqual(display_width("a‍b"), 2)  # ZWJ is zero

    def test_wide(self):
        self.assertEqual(display_width("中"), 2)
        self.assertEqual(display_width("Ａ"), 2)  # fullwidth A
        self.assertEqual(display_width("名称"), 4)

    def test_ambiguous_counts_one(self):
        # Box drawing is Ambiguous: policy is one column (non-CJK default).
        self.assertEqual(display_width("─│"), 2)

    @unittest.skipUnless(_HAS_WCWIDTH, "wcwidth not installed")
    def test_wcwidth_oracle_corpus(self):
        for text in CORPUS:
            if "\t" in text:
                continue  # wcwidth returns -1 for tabs; we reject them instead
            with self.subTest(text[:8]):
                self.assertEqual(display_width(text), wcwidth.wcswidth(text))

    @unittest.skipUnless(_HAS_WCWIDTH, "wcwidth not installed")
    def test_wcwidth_oracle_random_cells(self):
        import random

        rng = random.Random(20261023)
        alphabet = ("abcXYZ019 .,-中文名称café̂ＡＢ─━½①é")
        for _ in range(500):
            cell = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 12)))
            with self.subTest(cell[:6]):
                self.assertEqual(display_width(cell), wcwidth.wcswidth(cell))

    def test_control_rejected(self):
        with self.assertRaises(ValueError):
            display_width("a\x00b")
        with self.assertRaises(ValueError):
            display_width("tab\tinside")

    def test_measure_mode(self):
        out = self.tool.execute(mode="measure", text="名称ok")
        self.assertEqual(out["display_width"], 6)
        self.assertEqual(out["chars"], 4)


class FitRenderTest(unittest.TestCase):
    def setUp(self):
        self.tool = AsciiTableTool()

    def test_fit(self):
        out = self.tool.execute(mode="fit", rows=[["ab", "名称"], ["c", "x"]])
        self.assertEqual(out["column_widths"], [2, 4])

    def test_render_line_width_invariant(self):
        rows = [["名称", "value"], ["x", "café"], ["长长的文本内容", "1"]]
        for style in ("ascii", "rounded", "unicode", "markdown"):
            with self.subTest(style):
                out = self.tool.execute(mode="render", rows=rows, headers=["h1", "h2"], style=style)
                lines = out["table"].split("\n")
                widths = {display_width(ln) for ln in lines}
                self.assertEqual(len(widths), 1, f"{style}: {sorted(widths)} {lines}")

    @unittest.skipUnless(_HAS_WCWIDTH, "wcwidth not installed")
    def test_render_width_matches_wcwidth(self):
        out = self.tool.execute(
            mode="render", headers=["名称", "値"], rows=[["中", "①x"]],
            style="unicode", align=["center", "right"],
        )
        for line in out["table"].split("\n"):
            with self.subTest(line[:10]):
                self.assertEqual(display_width(line), wcwidth.wcswidth(line))

    def test_alignment(self):
        out = self.tool.execute(
            mode="render", headers=["col_a", "col_b", "col_c"],
            rows=[["x", "y", "z"]],
            style="markdown", align=["left", "center", "right"],
        )
        lines = out["table"].split("\n")
        self.assertEqual(lines[0], "| col_a | col_b | col_c |")
        self.assertEqual(lines[1], "| :---- | :---: | ----: |")
        self.assertEqual(lines[2], "| x     |   y   |     z |")

    def test_box_junctions(self):
        out = self.tool.execute(mode="render", headers=["a", "b"], rows=[["1", "2"]], style="unicode")
        lines = out["table"].split("\n")
        self.assertTrue(lines[0].startswith("┌") and "┬" in lines[0] and lines[0].endswith("┐"))
        self.assertTrue(lines[2].startswith("┼") and lines[2].endswith("┼"))
        self.assertTrue(lines[-1].startswith("└") and "┴" in lines[-1] and lines[-1].endswith("┘"))
        ascii_out = self.tool.execute(mode="render", headers=["a", "b"], rows=[["1", "2"]], style="ascii")
        self.assertEqual(ascii_out["table"].split("\n")[0], "+---+---+")

    @unittest.skipUnless(_HAS_WCWIDTH, "wcwidth not installed")
    def test_markdown_round_trip(self):
        rows = [["名称,逗号", "x"], ["a\"q", "中"], ["plain", "café"]]
        out = self.tool.execute(mode="render", headers=["h1", "h2"], rows=rows, style="markdown")
        lines = out["table"].split("\n")
        body = [ln.strip() for ln in lines[2:]]
        parsed = []
        for ln in body:
            cells = next(csv.reader(io.StringIO(ln), delimiter="|", quotechar='"'))
            parsed.append([c.strip() for c in cells if c.strip() != ""])
        self.assertEqual(parsed[0], ["名称,逗号", "x"])
        self.assertEqual(parsed[1], ['a"q', "中"])
        self.assertEqual(parsed[2], ["plain", "café"])

    def test_truncation_never_splits_wide(self):
        out = self.tool.execute(
            mode="render", rows=[["名称名称", "abcdef"]],
            headers=["c1", "c2"], style="ascii", max_col_width=5,
        )
        row = out["table"].split("\n")[3]
        self.assertIn("名称…", row)  # two wide chars fit the 4-col budget, ellipsis fifth
        self.assertIn("abcd…", row)
        widths = {display_width(ln) for ln in out["table"].split("\n")}
        self.assertEqual(len(widths), 1)

    def test_ragged_rows_padded(self):
        out = self.tool.execute(mode="render", rows=[["a", "b"], ["only-one"]], style="ascii")
        self.assertIn("| only-one |   |", out["table"])

    def test_no_headers_box(self):
        out = self.tool.execute(mode="render", rows=[["a"]], style="ascii")
        self.assertEqual(out["table"], "+---+\n| a |\n+---+")

    def test_markdown_header_note(self):
        out = self.tool.execute(mode="render", rows=[["a", "b"]], style="markdown")
        self.assertTrue(any("first row as the header" in n for n in out["notes"]))

    def test_determinism(self):
        a = self.tool.execute(mode="render", rows=[["中", "x"]], headers=["h", "k"], style="rounded")
        b = self.tool.execute(mode="render", rows=[["中", "x"]], headers=["h", "k"], style="rounded")
        self.assertEqual(a["table"], b["table"])


class WidthModelDivergenceTest(unittest.TestCase):
    """wcwidth 0.8+ collapses emoji ZWJ sequences to grapheme width; this
    tool sums per-character widths. Both models are legitimate; rendering
    stays aligned because measuring and padding use the same ruler."""

    @unittest.skipUnless(_HAS_WCWIDTH, "wcwidth not installed")
    def test_family_emoji_divergence_documented(self):
        family = "\U0001F468\u200d\U0001F469\u200d\U0001F467"
        flags = "\U0001F1FA\U0001F1F8\U0001F1EF\U0001F1F5"
        self.assertEqual(display_width(family), 6)
        self.assertEqual(wcwidth.wcswidth(family), 2)
        self.assertEqual(display_width(flags), 8)
        self.assertEqual(wcwidth.wcswidth(flags), 4)

    def test_rendering_aligned_despite_emoji(self):
        tool = AsciiTableTool()
        out = tool.execute(
            mode="render", headers=["h"], rows=[["\U0001F468\u200d\U0001F469"]],
            style="unicode",
        )
        widths = {display_width(ln) for ln in out["table"].split("\n")}
        self.assertEqual(len(widths), 1)


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.tool = AsciiTableTool()

    def test_bad_shapes(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows="not-a-list")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=[["ok"], ["bad", ["nested"]]])
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=None, headers=None)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=[["a"]], style="fancy")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=[["a"]], align="middle")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="measure", text=123)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="nope")

    def test_control_cells_rejected(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=[["a\x1b[0m"]])

    def test_caps(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="render", rows=[["x"] * 500])


if __name__ == "__main__":
    unittest.main()
