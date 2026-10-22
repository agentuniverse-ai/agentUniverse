#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_orgmode_tool.py

"""Offline unit tests for OrgModeTool.

The tool is built purely on the standard library (re + plain string
work) and never touches the network, so this suite runs fully offline.
Every assertion is deterministic and checked against hand-computed
ground truths: a nested outline exercising every feature (todo states,
priority cookies, tags, a :PROPERTIES: drawer with spans, src/quote
block immunity), custom #+TODO workflow declarations, the
todo_summary arithmetic and next-action rule, both strip variants,
and the strict error matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import OrgModeTool
from agentuniverse.agent.action.tool.common_tool.orgmode_tool import (
    OrgModeTool as DirectOrgModeTool,
)

SAMPLE_ORG = "\n".join(
    [
        "#+TITLE: Project Notes",
        "#+AUTHOR: Ada Lovelace",
        "#+FILETAGS: :work:planning:",
        "#+TODO: TODO DOING WAITING | DONE CANCELLED",
        "",
        "* TODO [#A] Launch product :urgent:q3:",
        ":PROPERTIES:",
        ":CUSTOM_ID: launch",
        ":END:",
        "Body text for launch.",
        "",
        "** DONE Write press release",
        "Some body.",
        "",
        "** DOING Schedule interviews :press:",
        "#+BEGIN_SRC org",
        "* this is not a heading",
        "#+TODO: FAKE | STATES",
        "#+END_SRC",
        "",
        "** WAITING Order cake",
        "* DONE Archive :home:",
        "#+BEGIN_QUOTE",
        "* also not a heading",
        "#+END_QUOTE",
    ]
)

# The flattened outline of SAMPLE_ORG, hand-computed. Subtree spans are
# 1-based inclusive and reach from the heading line to the line before
# the next heading of the same or shallower level.
SAMPLE_OUTLINE = [
    {
        "level": 1,
        "text": "Launch product",
        "todo_state": "TODO",
        "tags": ["urgent", "q3"],
        "priority": "A",
        "span": [6, 21],
        "drawers": [{"name": "PROPERTIES", "span": [7, 9]}],
    },
    {
        "level": 2,
        "text": "Write press release",
        "todo_state": "DONE",
        "tags": [],
        "priority": None,
        "span": [12, 14],
        "drawers": [],
    },
    {
        "level": 2,
        "text": "Schedule interviews",
        "todo_state": "DOING",
        "tags": ["press"],
        "priority": None,
        "span": [15, 20],
        "drawers": [],
    },
    {
        "level": 2,
        "text": "Order cake",
        "todo_state": "WAITING",
        "tags": [],
        "priority": None,
        "span": [21, 21],
        "drawers": [],
    },
    {
        "level": 1,
        "text": "Archive",
        "todo_state": "DONE",
        "tags": ["home"],
        "priority": None,
        "span": [22, 25],
        "drawers": [],
    },
]


def node(level, text, todo_state=None, tags=None, priority=None, span=None):
    """Build an expected outline node with defaults matching the tool."""
    return {
        "level": level,
        "text": text,
        "todo_state": todo_state,
        "tags": tags or [],
        "priority": priority,
        "span": span or [],
        "drawers": [],
    }


class OrgModeToolParseTest(unittest.TestCase):
    """Ground-truth tests for mode='parse'."""

    def setUp(self) -> None:
        self.tool = OrgModeTool()

    def test_parse_full_feature_outline(self) -> None:
        result = self.tool.execute(mode="parse", text=SAMPLE_ORG)
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["heading_count"], 5)
        self.assertEqual(result["outline"], SAMPLE_OUTLINE)

    def test_parse_meta_extraction(self) -> None:
        result = self.tool.execute(mode="parse", text=SAMPLE_ORG)
        self.assertEqual(
            result["meta"],
            {
                "title": "Project Notes",
                "author": "Ada Lovelace",
                "filetags": ["work", "planning"],
                "todo_workflow": {
                    "needs_action": ["TODO", "DOING", "WAITING"],
                    "done": ["DONE", "CANCELLED"],
                },
            },
        )

    def test_parse_src_and_quote_blocks_immune(self) -> None:
        # The fake heading and the #+TODO line inside #+BEGIN_SRC, and
        # the fake heading inside #+BEGIN_QUOTE, must stay content.
        result = self.tool.execute(mode="parse", text=SAMPLE_ORG)
        texts = [h["text"] for h in result["outline"]]
        self.assertNotIn("this is not a heading", texts)
        self.assertNotIn("also not a heading", texts)
        self.assertNotIn("FAKE", str(result["meta"]["todo_workflow"]))
        self.assertEqual(result["heading_count"], 5)

    def test_parse_default_workflow(self) -> None:
        result = self.tool.execute(mode="parse", text="* TODO a\n* DONE b\n* c\n")
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["TODO"], "done": ["DONE"]},
        )
        states = [h["todo_state"] for h in result["outline"]]
        self.assertEqual(states, ["TODO", "DONE", None])

    def test_parse_custom_workflow_with_shortcuts(self) -> None:
        org = (
            "#+TODO: TODO(t) DOING(d) | DONE(D) CANCELLED(c)\n"
            "* TODO one\n"
            "* DOING two\n"
            "* CANCELLED three\n"
        )
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["TODO", "DOING"], "done": ["DONE", "CANCELLED"]},
        )
        states = [h["todo_state"] for h in result["outline"]]
        self.assertEqual(states, ["TODO", "DOING", "CANCELLED"])

    def test_parse_seq_todo_quoted_keywords(self) -> None:
        org = '#+SEQ_TODO: "REPORT(r)" "BUG(b)" | FIXED(f)\n* REPORT x\n'
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["REPORT", "BUG"], "done": ["FIXED"]},
        )
        self.assertEqual(result["outline"][0]["todo_state"], "REPORT")

    def test_parse_multiple_todo_lines_union(self) -> None:
        org = (
            "#+TODO: TODO | DONE\n"
            "#+TYP_TODO: MEETING | HELD\n"
            "* TODO a\n"
            "* MEETING b\n"
            "* HELD c\n"
        )
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["TODO", "MEETING"], "done": ["DONE", "HELD"]},
        )

    def test_parse_todo_line_without_bar_all_needs_action(self) -> None:
        org = "#+TODO: OPEN WAITING\n* OPEN a\n* WAITING b\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["OPEN", "WAITING"], "done": []},
        )

    def test_parse_level_cap(self) -> None:
        org = "* level one\n************ very deep\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["outline"][1]["level"], 10)
        self.assertTrue(result["warnings"])
        self.assertIn("capped at 10", result["warnings"][0])
        self.assertIn("12 asterisks", result["warnings"][0])

    def test_parse_tags_variants(self) -> None:
        org = (
            "* Foo bar :a:b:c:\n"
            "* No tag colon: note:\n"
            "* Dash stays :has-dash:\n"
            "* TODO :urgent:\n"
        )
        result = self.tool.execute(mode="parse", text=org)
        first, second, third, fourth = result["outline"]
        self.assertEqual(first["tags"], ["a", "b", "c"])
        self.assertEqual(first["text"], "Foo bar")
        self.assertEqual(second["tags"], [])
        self.assertEqual(second["text"], "No tag colon: note:")
        self.assertEqual(third["tags"], [])
        self.assertEqual(third["text"], "Dash stays :has-dash:")
        self.assertEqual(fourth["tags"], ["urgent"])
        self.assertEqual(fourth["text"], "")
        self.assertEqual(fourth["todo_state"], "TODO")

    def test_parse_priority_variants(self) -> None:
        org = "* [#B] Medium task\n* TODO [#C] low\n* [#A]\n"
        result = self.tool.execute(mode="parse", text=org)
        first, second, third = result["outline"]
        self.assertEqual(
            (first["priority"], first["text"], first["todo_state"]),
            ("B", "Medium task", None),
        )
        self.assertEqual(
            (second["priority"], second["text"], second["todo_state"]),
            ("C", "low", "TODO"),
        )
        self.assertEqual(
            (third["priority"], third["text"], third["todo_state"]),
            ("A", "", None),
        )

    def test_parse_unknown_priority_cookie_kept_with_warning(self) -> None:
        result = self.tool.execute(mode="parse", text="* [#D] weird\n")
        heading = result["outline"][0]
        self.assertIsNone(heading["priority"])
        self.assertEqual(heading["text"], "[#D] weird")
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("[#D]", result["warnings"][0])

    def test_parse_empty_title_heading(self) -> None:
        result = self.tool.execute(mode="parse", text="* TODO\n")
        self.assertEqual(result["outline"][0]["todo_state"], "TODO")
        self.assertEqual(result["outline"][0]["text"], "")

    def test_parse_preamble_drawer(self) -> None:
        org = ":LOGBOOK:\n:END:\n* Heading\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result.get("preamble_drawers"),
            [{"name": "LOGBOOK", "span": [1, 2]}],
        )
        self.assertEqual(result["outline"][0]["drawers"], [])

    def test_parse_unclosed_drawer(self) -> None:
        org = "* Heading\n:PROPERTIES:\n:ID: xyz\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["outline"][0]["drawers"],
            [{"name": "PROPERTIES", "span": [2, 4]}],
        )
        self.assertTrue(any("never closed" in w for w in result["warnings"]))

    def test_parse_unclosed_block(self) -> None:
        org = "#+BEGIN_SRC python\n* not a heading\nstill content\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["heading_count"], 0)
        self.assertTrue(
            any("#+BEGIN_SRC" in w and "never closed" in w for w in result["warnings"])
        )

    def test_parse_duplicate_title_first_wins(self) -> None:
        org = "#+TITLE: First\n#+TITLE: Second\n* H\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["meta"]["title"], "First")
        self.assertTrue(any("duplicate #+TITLE" in w for w in result["warnings"]))

    def test_parse_empty_meta_lines_warned(self) -> None:
        org = "#+TITLE:\n#+AUTHOR:\n#+FILETAGS:\n* H\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertIsNone(result["meta"]["title"])
        self.assertIsNone(result["meta"]["author"])
        self.assertEqual(result["meta"]["filetags"], [])
        self.assertEqual(len(result["warnings"]), 3)

    def test_parse_empty_todo_line_keeps_default(self) -> None:
        org = "#+TODO:\n* TODO a\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["TODO"], "done": ["DONE"]},
        )
        self.assertTrue(any("without keywords" in w for w in result["warnings"]))

    def test_parse_unparsable_todo_token_keeps_default(self) -> None:
        org = "#+TODO: (x) |\n* TODO a\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(
            result["meta"]["todo_workflow"],
            {"needs_action": ["TODO"], "done": ["DONE"]},
        )
        self.assertTrue(any("unparsable todo keyword" in w for w in result["warnings"]))

    def test_parse_filetags_space_form_and_invalid_token(self) -> None:
        org = "#+FILETAGS: good b!d\n* H\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["meta"]["filetags"], ["good"])
        self.assertTrue(any("invalid characters" in w for w in result["warnings"]))

    def test_parse_unknown_keyword_line_is_silent(self) -> None:
        org = "#+OPTIONS: toc:2\n#+BOGUS: whatever\n* H\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertNotIn("warnings", result)

    def test_parse_lowercase_keywords(self) -> None:
        org = "#+title: Small Caps\n#+todo: TODO | DONE\n* TODO a\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["meta"]["title"], "Small Caps")
        self.assertEqual(result["outline"][0]["todo_state"], "TODO")

    def test_parse_crlf_normalized(self) -> None:
        org = "#+TITLE: T\r\n* Heading\r\nbody\r\n"
        result = self.tool.execute(mode="parse", text=org)
        self.assertEqual(result["meta"]["title"], "T")
        # The trailing newline becomes an empty 4th line, part of the
        # heading's subtree.
        self.assertEqual(result["outline"][0]["span"], [2, 4])


class OrgModeToolTodoSummaryTest(unittest.TestCase):
    """Ground-truth tests for mode='todo_summary'."""

    def setUp(self) -> None:
        self.tool = OrgModeTool()

    def test_todo_summary_ground_truth(self) -> None:
        result = self.tool.execute(mode="todo_summary", text=SAMPLE_ORG)
        self.assertEqual(
            result,
            {
                "mode": "todo_summary",
                "workflow": {
                    "needs_action": ["TODO", "DOING", "WAITING"],
                    "done": ["DONE", "CANCELLED"],
                },
                "heading_count": 5,
                "todo_heading_count": 5,
                "counts": {
                    "TODO": 1,
                    "DOING": 1,
                    "WAITING": 1,
                    "DONE": 2,
                    "CANCELLED": 0,
                },
                "done_headings": 2,
                "done_ratio": 0.4,
                "next_actions": [
                    {
                        "subtree": "Launch product",
                        "next_action": {
                            "level": 1,
                            "text": "Launch product",
                            "todo_state": "TODO",
                            "line": 6,
                        },
                    },
                    {"subtree": "Archive", "next_action": None},
                ],
            },
        )

    def test_todo_summary_next_action_descends_into_subtree(self) -> None:
        org = (
            "* Project A\n"
            "** DONE step 1\n"
            "** TODO step 2\n"
            "** TODO step 3\n"
            "* Project B\n"
            "** DONE everything\n"
        )
        result = self.tool.execute(mode="todo_summary", text=org)
        self.assertEqual(
            result["counts"], {"TODO": 2, "DONE": 2},
        )
        self.assertEqual(result["todo_heading_count"], 4)
        self.assertEqual(result["done_headings"], 2)
        self.assertAlmostEqual(result["done_ratio"], 0.5)
        # "Project A" itself carries no todo state, so its next action
        # is the first TODO child; "Project B" has none left.
        self.assertEqual(
            result["next_actions"],
            [
                {
                    "subtree": "Project A",
                    "next_action": {
                        "level": 2,
                        "text": "step 2",
                        "todo_state": "TODO",
                        "line": 3,
                    },
                },
                {"subtree": "Project B", "next_action": None},
            ],
        )

    def test_todo_summary_without_todo_headings(self) -> None:
        result = self.tool.execute(mode="todo_summary", text="* A\nbody\n* B\n")
        self.assertEqual(result["todo_heading_count"], 0)
        self.assertIsNone(result["done_ratio"])
        self.assertEqual(result["counts"], {"TODO": 0, "DONE": 0})
        self.assertEqual(
            result["next_actions"],
            [
                {"subtree": "A", "next_action": None},
                {"subtree": "B", "next_action": None},
            ],
        )

    def test_todo_summary_without_level_one_headings(self) -> None:
        org = "** TODO deep start\n** DONE deeper\n"
        result = self.tool.execute(mode="todo_summary", text=org)
        self.assertEqual(
            result["next_actions"],
            [
                {
                    "subtree": None,
                    "next_action": {
                        "level": 2,
                        "text": "deep start",
                        "todo_state": "TODO",
                        "line": 1,
                    },
                }
            ],
        )

    def test_todo_summary_empty_outline(self) -> None:
        result = self.tool.execute(mode="todo_summary", text="just body text\n")
        self.assertEqual(result["heading_count"], 0)
        self.assertEqual(result["next_actions"], [])
        self.assertIsNone(result["done_ratio"])


class OrgModeToolStripTest(unittest.TestCase):
    """Ground-truth tests for mode='strip'."""

    def setUp(self) -> None:
        self.tool = OrgModeTool()

    def test_strip_default(self) -> None:
        result = self.tool.execute(mode="strip", text=SAMPLE_ORG)
        self.assertEqual(result["mode"], "strip")
        self.assertFalse(result["body_only"])
        self.assertEqual(result["line_count"], 14)
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "",
                    "* TODO [#A] Launch product :urgent:q3:",
                    "Body text for launch.",
                    "",
                    "** DONE Write press release",
                    "Some body.",
                    "",
                    "** DOING Schedule interviews :press:",
                    "* this is not a heading",
                    "#+TODO: FAKE | STATES",
                    "",
                    "** WAITING Order cake",
                    "* DONE Archive :home:",
                    "* also not a heading",
                ]
            ),
        )

    def test_strip_body_only(self) -> None:
        result = self.tool.execute(mode="strip", text=SAMPLE_ORG, body_only=True)
        self.assertTrue(result["body_only"])
        self.assertEqual(result["line_count"], 9)
        self.assertEqual(
            result["result"],
            "\n".join(
                [
                    "",
                    "Body text for launch.",
                    "",
                    "Some body.",
                    "",
                    "* this is not a heading",
                    "#+TODO: FAKE | STATES",
                    "",
                    "* also not a heading",
                ]
            ),
        )

    def test_strip_body_only_false_is_default(self) -> None:
        explicit = self.tool.execute(mode="strip", text=SAMPLE_ORG, body_only=False)
        default = self.tool.execute(mode="strip", text=SAMPLE_ORG)
        self.assertEqual(explicit, default)

    def test_strip_empty_outline(self) -> None:
        # Text without org syntax round-trips unchanged (the trailing
        # newline becomes an empty kept line).
        result = self.tool.execute(mode="strip", text="plain\ntext\n")
        self.assertEqual(result["result"], "plain\ntext\n")

    def test_strip_reports_unclosed_drawer_warning(self) -> None:
        # The drawer never closes, so it swallows the rest of the file
        # (warned) — only the heading line survives.
        result = self.tool.execute(
            mode="strip", text="* H\n:PROPERTIES:\n:ID: x\nbody\n"
        )
        self.assertEqual(result["result"], "* H")
        self.assertTrue(any("never closed" in w for w in result["warnings"]))


class OrgModeToolValidationTest(unittest.TestCase):
    """Strict input validation — the error matrix."""

    def setUp(self) -> None:
        self.tool = OrgModeTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="org", text="* H\n")
        self.assert_invalid(mode=None, text="* H\n")
        self.assert_invalid(mode=123, text="* H\n")
        self.assert_invalid(mode="PARSE", text="* H\n")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"* H", ["* H"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)
                self.assert_invalid(mode="todo_summary", text=bad)
                self.assert_invalid(mode="strip", text=bad)

    def test_empty_text_rejected(self) -> None:
        for mode in ("parse", "todo_summary", "strip"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="parse", text=oversized)
        ok = self.tool.execute(mode="parse", text="a" * 100_000)
        self.assertEqual(ok["heading_count"], 0)

    def test_invalid_body_only(self) -> None:
        self.assert_invalid(mode="strip", text="* H\n", body_only="yes")
        self.assert_invalid(mode="strip", text="* H\n", body_only=1)
        self.assert_invalid(mode="parse", text="* H\n", body_only="true")

    def test_body_only_boolean_and_none_accepted(self) -> None:
        for value in (True, False, None):
            with self.subTest(body_only=value):
                result = self.tool.execute(
                    mode="strip", text="* H\nbody\n", body_only=value
                )
                self.assertEqual(result["body_only"], bool(value))


class OrgModeToolRegistrationTest(unittest.TestCase):
    """Packaging / registration."""

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectOrgModeTool, OrgModeTool)
        tool = OrgModeTool()
        self.assertEqual(tool.name, "orgmode_tool")
        self.assertIn("org-mode", tool.description)
        self.assertEqual(OrgModeTool.MODES, ("parse", "todo_summary", "strip"))
        self.assertEqual(OrgModeTool.MAX_LEVEL, 10)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("OrgModeTool", __all__)


if __name__ == "__main__":
    unittest.main()
