#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_conflict_parser_tool.py

"""Offline unit tests for ConflictParserTool.

The tool is built purely on the standard library (re only) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: parse results are checked against literal expected
region dicts, stats against hand-computed arithmetic, resolve / strip
output against exact ground-truth strings (including the CRLF variants),
and errors against a full matrix of both ValueError shapes and
structured error payloads.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import ConflictParserTool
from agentuniverse.agent.action.tool.common_tool.conflict_parser_tool import (
    ConflictParserTool as DirectConflictParserTool,
)

# --------------------------------------------------------------------- #
# Ground-truth documents (literal, independent of any git invocation)
# --------------------------------------------------------------------- #

# One merge-style conflict with branch labels, surrounded by clean text.
MERGE_DOC = (
    "import os\n"
    "<<<<<<< HEAD\n"
    "size = 1\n"
    "=======\n"
    "size = 2\n"
    ">>>>>>> feature\n"
    "print(size)\n"
)

# One diff3-style conflict carrying a base section.
DIFF3_DOC = (
    "alpha\n"
    "<<<<<<< ours\n"
    "beta\n"
    "||||||| base\n"
    "alpha2\n"
    "=======\n"
    "gamma\n"
    ">>>>>>> theirs\n"
    "delta\n"
)

# Two merge-style conflicts with clean text in between; the first has
# identical ours/theirs sides (trivially resolvable).
MULTI_DOC = (
    "head\n"
    "<<<<<<< HEAD\n"
    "same\n"
    "=======\n"
    "same\n"
    ">>>>>>> other\n"
    "mid\n"
    "<<<<<<< HEAD\n"
    "a\n"
    "b\n"
    "=======\n"
    "z\n"
    ">>>>>>> other\n"
    "tail\n"
)

# A merge-style conflict followed by a diff3-style conflict (no clean
# text before the first conflict).
MIXED_DOC = (
    "<<<<<<< HEAD\n"
    "o1\n"
    "=======\n"
    "t1\n"
    ">>>>>>> x\n"
    "mid\n"
    "<<<<<<< HEAD\n"
    "o2\n"
    "|||||||\n"
    "b2\n"
    "=======\n"
    "t2\n"
    ">>>>>>> x\n"
)

# Conflict-free documents used for the byte-identical identity checks.
CLEAN_LF = "keep\nthis\ntext\nexactly\n"
CLEAN_CRLF = "keep\r\nthis\r\ntext\r\n\r\nexactly"

# Conflict whose closing marker has no trailing newline.
DOC_NO_EOL = "a\n<<<<<<< HEAD\nX\n=======\nY\n>>>>>>> t"


class ConflictParserToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ConflictParserTool."""

    def setUp(self) -> None:
        self.tool = ConflictParserTool()

    # ------------------------------------------------------------------ #
    # parse mode — ground-truth region dicts
    # ------------------------------------------------------------------ #

    def test_parse_merge_style_exact_payload(self) -> None:
        result = self.tool.execute(mode="parse", text=MERGE_DOC)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "conflicts": [
                    {
                        "start_line": 2,
                        "ours": ["size = 1"],
                        "base": None,
                        "theirs": ["size = 2"],
                        "marker_style": "merge",
                        "resolved_flag": False,
                    }
                ],
                "conflict_count": 1,
                "clean_lines": 2,
                "total": 7,
            },
        )

    def test_parse_diff3_style_exact_payload(self) -> None:
        result = self.tool.execute(mode="parse", text=DIFF3_DOC)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "conflicts": [
                    {
                        "start_line": 2,
                        "ours": ["beta"],
                        "base": ["alpha2"],
                        "theirs": ["gamma"],
                        "marker_style": "diff3",
                        "resolved_flag": False,
                    }
                ],
                "conflict_count": 1,
                "clean_lines": 2,
                "total": 9,
            },
        )

    def test_parse_multi_conflict_with_intermixed_clean_text(self) -> None:
        result = self.tool.execute(mode="parse", text=MULTI_DOC)
        self.assertEqual(
            [conflict["start_line"] for conflict in result["conflicts"]],
            [2, 8],
        )
        self.assertEqual(result["conflicts"][0]["ours"], ["same"])
        self.assertEqual(result["conflicts"][0]["theirs"], ["same"])
        self.assertEqual(result["conflicts"][1]["ours"], ["a", "b"])
        self.assertEqual(result["conflicts"][1]["theirs"], ["z"])
        self.assertEqual(result["conflict_count"], 2)
        # clean_lines arithmetic: 3 clean lines (1, 7, 14) + 5 + 6
        # conflict-block lines == 14 total lines.
        self.assertEqual(result["clean_lines"], 3)
        self.assertEqual(result["total"], 14)
        self.assertEqual(
            result["clean_lines"]
            + sum(
                5 if conflict["start_line"] == 2 else 6
                for conflict in result["conflicts"]
            ),
            result["total"],
        )

    def test_parse_marker_label_variants(self) -> None:
        # Unlabeled markers and markers without the optional space.
        doc = "<<<<<<<\nX\n=======\nY\n>>>>>>>\n"
        result = self.tool.execute(mode="parse", text=doc)
        self.assertEqual(result["conflict_count"], 1)
        self.assertEqual(result["conflicts"][0]["ours"], ["X"])
        self.assertEqual(result["conflicts"][0]["theirs"], ["Y"])
        # "<<<<<<<HEAD" (no space, 8 '<') still opens a conflict.
        doc_nospace = "<<<<<<<HEAD\nX\n=======\nY\n>>>>>>>branch\n"
        result = self.tool.execute(mode="parse", text=doc_nospace)
        self.assertEqual(result["conflict_count"], 1)

    def test_parse_eight_equals_and_labeled_separator_are_content(self) -> None:
        # Only a bare exactly-seven-character '=======' line separates;
        # '========' and '======= label' are ordinary content lines.
        doc = "<<<<<<< HEAD\n========\n======= label\n=======\nt\n>>>>>>> x\n"
        result = self.tool.execute(mode="parse", text=doc)
        self.assertEqual(
            result["conflicts"][0]["ours"], ["========", "======= label"]
        )
        self.assertEqual(result["conflicts"][0]["theirs"], ["t"])

    def test_parse_empty_ours_section(self) -> None:
        doc = "<<<<<<< H\n=======\nT\n>>>>>>> x\n"
        result = self.tool.execute(mode="parse", text=doc)
        self.assertEqual(result["conflicts"][0]["ours"], [])
        self.assertEqual(result["conflicts"][0]["theirs"], ["T"])

    def test_parse_empty_text(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", text=""),
            {
                "mode": "parse",
                "conflicts": [],
                "conflict_count": 0,
                "clean_lines": 0,
                "total": 0,
            },
        )

    def test_parse_clean_text(self) -> None:
        result = self.tool.execute(mode="parse", text=CLEAN_LF)
        self.assertEqual(result["conflict_count"], 0)
        self.assertEqual(result["clean_lines"], 4)
        self.assertEqual(result["total"], 4)

    # ------------------------------------------------------------------ #
    # stats mode — hand-computed arithmetic
    # ------------------------------------------------------------------ #

    def test_stats_multi_doc_exact_payload(self) -> None:
        result = self.tool.execute(mode="stats", text=MULTI_DOC)
        self.assertEqual(
            result,
            {
                "mode": "stats",
                "conflict_count": 2,
                "ours_lines": 3,
                "theirs_lines": 2,
                "base_lines": 0,
                "identical_count": 1,
                "clean_lines": 3,
                "total": 14,
                "overlap_hint": (
                    "1 of 2 conflicts have identical 'ours' and 'theirs' "
                    "sides and are trivially resolvable (choose either "
                    "side, or choose='identical')"
                ),
            },
        )

    def test_stats_mixed_doc_sums_base_lines_of_diff3_only(self) -> None:
        result = self.tool.execute(mode="stats", text=MIXED_DOC)
        self.assertEqual(result["conflict_count"], 2)
        self.assertEqual(result["ours_lines"], 2)
        self.assertEqual(result["theirs_lines"], 2)
        self.assertEqual(result["base_lines"], 1)
        self.assertEqual(result["identical_count"], 0)
        self.assertEqual(result["clean_lines"], 1)
        self.assertEqual(result["total"], 13)
        self.assertIn("0 of 2", result["overlap_hint"])

    def test_stats_clean_and_empty_text(self) -> None:
        for text, total in ((CLEAN_LF, 4), ("", 0)):
            result = self.tool.execute(mode="stats", text=text)
            self.assertEqual(result["conflict_count"], 0)
            self.assertEqual(result["ours_lines"], 0)
            self.assertEqual(result["theirs_lines"], 0)
            self.assertEqual(result["base_lines"], 0)
            self.assertEqual(result["identical_count"], 0)
            self.assertEqual(result["total"], total)
            self.assertIn("0 of 0", result["overlap_hint"])

    # ------------------------------------------------------------------ #
    # resolve mode — every choose variant against exact strings
    # ------------------------------------------------------------------ #

    def test_resolve_choose_ours(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 0, "choose": "ours"}],
        )
        self.assertEqual(
            result,
            {
                "mode": "resolve",
                "result": "import os\nsize = 1\nprint(size)\n",
                "resolved_count": 1,
                "remaining_conflicts": 0,
            },
        )

    def test_resolve_choose_theirs(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 0, "choose": "theirs"}],
        )
        self.assertEqual(
            result["result"], "import os\nsize = 2\nprint(size)\n"
        )
        self.assertEqual(result["remaining_conflicts"], 0)

    def test_resolve_choose_base_on_diff3(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=DIFF3_DOC,
            resolutions=[{"index": 0, "choose": "base"}],
        )
        self.assertEqual(result["result"], "alpha\nalpha2\ndelta\n")
        self.assertEqual(result["remaining_conflicts"], 0)

    def test_resolve_custom_text(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[
                {"index": 0, "choose": "custom", "custom_text": "size = 3"}
            ],
        )
        # custom_text is inserted verbatim plus the closing marker's
        # line terminator.
        self.assertEqual(
            result["result"], "import os\nsize = 3\nprint(size)\n"
        )

    def test_resolve_empty_custom_text_removes_block(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 0, "choose": "custom", "custom_text": ""}],
        )
        self.assertEqual(result["result"], "import os\nprint(size)\n")

    def test_resolve_identical_shortcut(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MULTI_DOC,
            resolutions=[{"index": 0, "choose": "identical"}],
        )
        self.assertEqual(
            result["result"],
            "head\nsame\nmid\n"
            "<<<<<<< HEAD\na\nb\n=======\nz\n>>>>>>> other\n"
            "tail\n",
        )
        self.assertEqual(result["resolved_count"], 1)
        self.assertEqual(result["remaining_conflicts"], 1)

    def test_resolve_multiple_conflicts_in_index_order(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MULTI_DOC,
            resolutions=[
                {"index": 1, "choose": "theirs"},
                {"index": 0, "choose": "identical"},  # out of order on purpose
            ],
        )
        self.assertEqual(result["result"], "head\nsame\nmid\nz\ntail\n")
        self.assertEqual(result["resolved_count"], 2)
        self.assertEqual(result["remaining_conflicts"], 0)

    def test_resolve_unresolved_conflicts_survive_verbatim(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MULTI_DOC,
            resolutions=[{"index": 1, "choose": "ours"}],
        )
        self.assertEqual(
            result["result"],
            "head\n"
            "<<<<<<< HEAD\nsame\n=======\nsame\n>>>>>>> other\n"
            "mid\na\nb\ntail\n",
        )
        self.assertEqual(result["remaining_conflicts"], 1)

    def test_resolve_choose_ours_on_empty_ours_deletes_conflict(self) -> None:
        doc = "<<<<<<< H\n=======\nT\n>>>>>>> x\n"
        result = self.tool.execute(
            mode="resolve", text=doc, resolutions=[{"index": 0, "choose": "ours"}]
        )
        self.assertEqual(result["result"], "")

    def test_resolve_no_trailing_newline_at_eof(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=DOC_NO_EOL,
            resolutions=[{"index": 0, "choose": "theirs"}],
        )
        self.assertEqual(result["result"], "a\nY\n")
        result = self.tool.execute(
            mode="resolve",
            text=DOC_NO_EOL,
            resolutions=[
                {"index": 0, "choose": "custom", "custom_text": "Z"}
            ],
        )
        self.assertEqual(result["result"], "a\nZ")

    def test_resolve_identity_on_clean_text(self) -> None:
        for text in (CLEAN_LF, CLEAN_CRLF, DOC_NO_EOL[:2] + "\nlast"):
            result = self.tool.execute(mode="resolve", text=text, resolutions=[])
            self.assertEqual(result["result"], text)
            self.assertEqual(result["remaining_conflicts"], 0)

    def test_resolve_empty_resolutions_leave_conflicts(self) -> None:
        result = self.tool.execute(
            mode="resolve", text=MERGE_DOC, resolutions=[]
        )
        self.assertEqual(result["result"], MERGE_DOC)
        self.assertEqual(result["resolved_count"], 0)
        self.assertEqual(result["remaining_conflicts"], 1)

    def test_resolve_on_empty_text(self) -> None:
        result = self.tool.execute(mode="resolve", text="", resolutions=[])
        self.assertEqual(
            result,
            {
                "mode": "resolve",
                "result": "",
                "resolved_count": 0,
                "remaining_conflicts": 0,
            },
        )

    # ------------------------------------------------------------------ #
    # resolve mode — structured (content-level) errors
    # ------------------------------------------------------------------ #

    def test_resolve_base_on_merge_style_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 0, "choose": "base"}],
        )
        self.assertEqual(result["mode"], "resolve")
        self.assertEqual(result["error"]["type"], "invalid_resolution")
        self.assertEqual(result["error"]["index"], 0)
        self.assertIn("no base section", result["error"]["message"])

    def test_resolve_identical_with_differing_sides_is_error(self) -> None:
        result = self.tool.execute(
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 0, "choose": "identical"}],
        )
        self.assertEqual(result["error"]["type"], "invalid_resolution")
        self.assertEqual(result["error"]["index"], 0)
        self.assertIn("differing", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # strip mode — naive lossy fallback
    # ------------------------------------------------------------------ #

    def test_strip_keep_ours_default(self) -> None:
        result = self.tool.execute(mode="strip", text=MIXED_DOC)
        self.assertEqual(
            result,
            {
                "mode": "strip",
                "keep": "ours",
                "result": "o1\nmid\no2\n",
            },
        )

    def test_strip_keep_theirs(self) -> None:
        result = self.tool.execute(
            mode="strip", text=MIXED_DOC, keep="theirs"
        )
        self.assertEqual(result["keep"], "theirs")
        # Lossy: the base and ours sections are gone without inspection.
        self.assertEqual(result["result"], "t1\nmid\nt2\n")

    def test_strip_identity_on_clean_text(self) -> None:
        for text in (CLEAN_LF, CLEAN_CRLF, "no trailing newline", ""):
            self.assertEqual(
                self.tool.execute(mode="strip", text=text)["result"], text
            )

    def test_strip_no_trailing_newline_at_eof(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="strip", text=DOC_NO_EOL)["result"], "a\nX\n"
        )

    # ------------------------------------------------------------------ #
    # CRLF handling
    # ------------------------------------------------------------------ #

    def test_parse_crlf_document(self) -> None:
        doc = (
            "x\r\n<<<<<<< HEAD\r\nours1\r\n=======\r\ntheirs1\r\n>>>>>>> b\r\ny\r\n"
        )
        result = self.tool.execute(mode="parse", text=doc)
        self.assertEqual(result["conflicts"][0]["ours"], ["ours1"])
        self.assertEqual(result["conflicts"][0]["theirs"], ["theirs1"])
        self.assertEqual(result["conflicts"][0]["start_line"], 2)
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["clean_lines"], 2)

    def test_resolve_preserves_crlf(self) -> None:
        doc = (
            "x\r\n<<<<<<< HEAD\r\nours1\r\n=======\r\ntheirs1\r\n>>>>>>> b\r\ny\r\n"
        )
        result = self.tool.execute(
            mode="resolve",
            text=doc,
            resolutions=[{"index": 0, "choose": "theirs"}],
        )
        self.assertEqual(result["result"], "x\r\ntheirs1\r\ny\r\n")

    def test_strip_preserves_crlf(self) -> None:
        doc = "x\r\n<<<<<<< HEAD\r\nours1\r\n=======\r\ntheirs1\r\n>>>>>>> b\r\ny\r\n"
        self.assertEqual(
            self.tool.execute(mode="strip", text=doc)["result"],
            "x\r\nours1\r\ny\r\n",
        )

    def test_mixed_line_endings_survive_resolve_verbatim(self) -> None:
        # A clean line with a lone \r terminator plus \n lines: every
        # token keeps its own terminator through resolve.
        doc = "keep\r<<<<<<< HEAD\nours\n=======\ntheirs\n>>>>>>> x\n"
        result = self.tool.execute(mode="resolve", text=doc, resolutions=[])
        self.assertEqual(result["result"], doc)

    # ------------------------------------------------------------------ #
    # Unclosed / stray markers — structured errors with the line
    # ------------------------------------------------------------------ #

    def assertParseError(
        self, doc: str, error_type: str, line: int, mode: str = "parse"
    ) -> None:
        result = self.tool.execute(mode=mode, text=doc)
        self.assertEqual(result["mode"], mode)
        self.assertEqual(result["error"]["type"], error_type)
        self.assertEqual(result["error"]["line"], line)

    def test_unclosed_eof_in_ours_section(self) -> None:
        self.assertParseError(
            "intro\n<<<<<<< HEAD\nours\n",
            "unclosed_conflict",
            2,
        )

    def test_unclosed_eof_before_closing_marker(self) -> None:
        self.assertParseError(
            "<<<<<<< HEAD\nours\n=======\ntheirs\n",
            "unclosed_conflict",
            1,
        )

    def test_unclosed_closing_marker_before_separator(self) -> None:
        self.assertParseError(
            "<<<<<<< HEAD\nours\n>>>>>>> x\n",
            "unclosed_conflict",
            1,
        )

    def test_unclosed_second_opener_before_separator(self) -> None:
        self.assertParseError(
            "<<<<<<< A\nx\n<<<<<<< B\n",
            "unclosed_conflict",
            1,
        )

    def test_unclosed_diff3_eof_in_base_section(self) -> None:
        self.assertParseError(
            "<<<<<<< A\nx\n|||||||\nbase\n",
            "unclosed_conflict",
            1,
        )

    def test_unclosed_stray_opener_inside_theirs_section(self) -> None:
        self.assertParseError(
            "<<<<<<< A\nx\n=======\nt\n<<<<<<< B\n",
            "unclosed_conflict",
            1,
        )

    def test_stray_separator_outside_conflict(self) -> None:
        self.assertParseError("a\n=======\nb\n", "unexpected_marker", 2)

    def test_stray_closing_marker_outside_conflict(self) -> None:
        self.assertParseError(">>>>>>> x\n", "unexpected_marker", 1)

    def test_stray_base_marker_outside_conflict(self) -> None:
        self.assertParseError(
            "a\n|||||||\n", "unexpected_marker", 2
        )

    def test_parse_errors_surface_in_every_mode(self) -> None:
        bad = "a\n<<<<<<< HEAD\nx\n"
        for mode in ("parse", "stats", "strip"):
            self.assertParseError(bad, "unclosed_conflict", 2, mode=mode)
        result = self.tool.execute(
            mode="resolve", text=bad, resolutions=[]
        )
        self.assertEqual(result["error"]["type"], "unclosed_conflict")

    # ------------------------------------------------------------------ #
    # ValueError matrix (strict parameter validation)
    # ------------------------------------------------------------------ #

    def assertInvalid(self, message_fragment: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn(
            "conflict_parser_tool:", str(ctx.exception)
        )
        self.assertIn(message_fragment, str(ctx.exception))

    def test_invalid_mode(self) -> None:
        self.assertInvalid("mode must be one of", mode="merge", text="a\n")

    def test_invalid_text_types(self) -> None:
        for bad_text in (None, 123, True, ["line"]):
            self.assertInvalid("text must be a string", mode="parse", text=bad_text)

    def test_invalid_text_too_large(self) -> None:
        self.assertInvalid(
            "exceeds the 100,000-character limit",
            mode="parse",
            text="a" * 100_001,
        )

    def test_invalid_resolutions_shapes(self) -> None:
        cases = [
            (None, "resolutions must be a list"),
            ("ours", "resolutions must be a list"),
            (42, "resolutions must be a list"),
            ([13], "resolutions[0] must be a dict"),
            ([{}], "index must be a non-negative integer"),
            ([{"index": "0", "choose": "ours"}], "non-negative integer"),
            ([{"index": True, "choose": "ours"}], "non-negative integer"),
            ([{"index": -1, "choose": "ours"}], "non-negative integer"),
            ([{"index": 0}], "choose must be one of"),
            ([{"index": 0, "choose": "both"}], "choose must be one of"),
            (
                [{"index": 0, "choose": "custom"}],
                "requires a string custom_text",
            ),
            (
                [{"index": 0, "choose": "custom", "custom_text": 5}],
                "requires a string custom_text",
            ),
            (
                [{"index": 0, "choose": "ours", "custom_text": "x"}],
                "only accepted with choose='custom'",
            ),
            (
                [{"index": 0, "choose": "ours"}, {"index": 0, "choose": "base"}],
                "duplicated",
            ),
        ]
        for resolutions, fragment in cases:
            self.assertInvalid(
                fragment,
                mode="resolve",
                text=MERGE_DOC,
                resolutions=resolutions,
            )

    def test_invalid_resolution_index_out_of_range(self) -> None:
        self.assertInvalid(
            "valid indices are 0..0",
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[{"index": 1, "choose": "ours"}],
        )
        self.assertInvalid(
            "contains no conflicts",
            mode="resolve",
            text=CLEAN_LF,
            resolutions=[{"index": 0, "choose": "ours"}],
        )

    def test_invalid_keep_and_cross_mode_parameters(self) -> None:
        self.assertInvalid(
            "keep must be one of", mode="strip", text="a\n", keep="base"
        )
        self.assertInvalid(
            "keep is only accepted in the strip mode",
            mode="parse",
            text="a\n",
            keep="ours",
        )
        self.assertInvalid(
            "resolutions is only accepted in the resolve mode",
            mode="parse",
            text="a\n",
            resolutions=[],
        )
        self.assertInvalid(
            "resolutions is only accepted in the resolve mode",
            mode="stats",
            text="a\n",
            resolutions=[{"index": 0, "choose": "ours"}],
        )

    def test_custom_text_too_large(self) -> None:
        self.assertInvalid(
            "custom_text exceeds the 100,000-character limit",
            mode="resolve",
            text=MERGE_DOC,
            resolutions=[
                {"index": 0, "choose": "custom", "custom_text": "x" * 100_001}
            ],
        )

    # ------------------------------------------------------------------ #
    # Packaging
    # ------------------------------------------------------------------ #

    def test_default_tool_attributes(self) -> None:
        self.assertEqual(self.tool.name, "conflict_parser_tool")
        self.assertIn("merge/diff3", self.tool.description)
        self.assertIs(DirectConflictParserTool, ConflictParserTool)


if __name__ == "__main__":
    unittest.main()
