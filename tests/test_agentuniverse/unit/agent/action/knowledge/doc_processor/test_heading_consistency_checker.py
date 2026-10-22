# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @FileName: test_heading_consistency_checker.py

import copy
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.heading_consistency_checker import HeadingConsistencyChecker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A well-formed document: every nesting step skips exactly one level and
# every title is unique — no findings, score 1.0.
CLEAN_DOC = (
    "# Deployment Guide\n"
    "intro paragraph\n"
    "## Requirements\n"
    "some text\n"
    "### Hardware\n"
    "notes\n"
    "## Installation\n"
    "steps follow\n"
    "### Linux\n"
    "### Windows\n"
    "## Troubleshooting\n"
)

# One document exercising every always-on check exactly once except
# max_depth_exceeded; finding arithmetic is hand-verified below.
COMBINED_DOC = (
    "# Guide\n"          # line 1  h1
    "#### Deep\n"        # line 2  h4 after h1  -> level_jump (skip 3)
    "## Setup\n"         # line 3
    "## setup\n"         # line 4  casefold duplicate of line 3
    "#\n"                # line 5  empty heading
    "##### Deeper\n"     # line 6  h5 after the h1 on line 5 -> level_jump (skip 4)
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestHeadingConsistencyChecker(unittest.TestCase):
    """Comprehensive test suite for HeadingConsistencyChecker."""

    def setUp(self):
        self.checker = HeadingConsistencyChecker()
        self.query = Query(query_str="heading qa")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _run(self, text):
        """Process one document and return it after stamping."""
        doc = _doc(text)
        result = self.checker.process_docs([doc], self.query)
        return result[0]

    def _kinds(self, text):
        """Finding kinds for one document, in stamped order."""
        return [f["kind"] for f in self._run(text).metadata["heading_issues"]]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: max_level 6 (check off), no first-heading flag,
        cap 100 and the four documented metadata keys."""
        c = HeadingConsistencyChecker()
        self.assertEqual(c.max_level, 6)
        self.assertFalse(c.flag_first_not_h1)
        self.assertEqual(c.max_findings, 100)
        self.assertEqual(c.issues_key, "heading_issues")
        self.assertEqual(c.counts_key, "heading_issue_counts")
        self.assertEqual(c.total_key, "heading_issue_total")
        self.assertEqual(c.score_key, "heading_score")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'heading_consistency_checker',
            'description': 'heading qa',
            'max_level': 3,
            'flag_first_not_h1': True,
            'max_findings': 5,
            'issues_key': 'headings',
            'counts_key': 'heading_counts',
            'total_key': 'heading_total',
            'score_key': 'heading_health',
        })
        c = HeadingConsistencyChecker()
        c._initialize_by_component_configer(configer)
        self.assertEqual(c.max_level, 3)
        self.assertTrue(c.flag_first_not_h1)
        self.assertEqual(c.max_findings, 5)
        self.assertEqual(c.issues_key, "headings")
        self.assertEqual(c.counts_key, "heading_counts")
        self.assertEqual(c.total_key, "heading_total")
        self.assertEqual(c.score_key, "heading_health")
        self.assertEqual(c.name, "heading_consistency_checker")

    def test_invalid_configuration_raises(self):
        """Out-of-range max_level / max_findings, non-integer values and
        non-string metadata keys all fail at load time."""
        base = {
            'name': 'c', 'description': 'd',
            'max_level': 6, 'flag_first_not_h1': False,
            'max_findings': 100, 'issues_key': 'heading_issues',
            'counts_key': 'heading_issue_counts',
            'total_key': 'heading_issue_total', 'score_key': 'heading_score',
        }
        for key, value in (
            ('max_level', 0),
            ('max_level', 7),
            ('max_level', 2.5),
            ('max_level', True),
            ('max_findings', 0),
            ('max_findings', -1),
            ('max_findings', 1.5),
            ('max_findings', True),
            ('issues_key', 5),
            ('counts_key', ['x']),
            ('total_key', None.__class__),
            ('score_key', 3.5),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                HeadingConsistencyChecker()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== ATX parsing and fence immunity ==========

    def test_parse_atx_headings(self):
        """Levels, titles, line numbers, leading spaces up to three,
        closing sequences and tab separators parse per the ATX rules."""
        headings = HeadingConsistencyChecker._parse_headings(
            "# One\n"
            "paragraph text\n"
            "## Two ##\n"
            "   ### Three\n"      # three leading spaces: still a heading
            "##\tTabbed\n"        # tab after the hashes is a separator
            "#### Four #\n"
        )
        self.assertEqual(headings, [
            (1, "One", 1),
            (2, "Two", 3),
            (3, "Three", 4),
            (2, "Tabbed", 5),
            (4, "Four", 6),
        ])

    def test_non_heading_lines_ignored(self):
        """Seven hashes, '#5 bolts', four-space indentation and setext
        underlines are not ATX headings."""
        headings = HeadingConsistencyChecker._parse_headings(
            "####### seven hashes\n"
            "#5 bolts\n"
            "    # indented code block\n"
            "Setext Title\n"
            "============\n"
            "## Real\n"
        )
        self.assertEqual(headings, [(2, "Real", 6)])

    def test_fence_immunity_backticks(self):
        """Heading-like lines inside a backtick fence are ignored and do
        not disturb level tracking outside it."""
        doc = self._run(
            "# Title\n"
            "```python\n"
            "# not a heading (comment)\n"
            "## nor this\n"
            "```\n"
            "## Sub\n"
        )
        self.assertEqual(doc.metadata["heading_issue_total"], 0)
        self.assertEqual(doc.metadata["heading_score"], 1.0)

    def test_fence_immunity_tildes_and_nested_markers(self):
        """Tilde fences work; a shorter or wrong-character fence line
        does not close a fence; the fence's own line is never a heading."""
        headings = HeadingConsistencyChecker._parse_headings(
            "~~~\n"
            "# fake inside tilde fence\n"
            "```\n"                # wrong character: does not close ~~~
            "~~~~\n"               # longer tilde run closes it
            "````\n"               # opens a 4-backtick fence
            "```\n"                # shorter: does not close it
            "# still inside\n"
            "````\n"
            "# Real\n"
        )
        self.assertEqual(headings, [(1, "Real", 9)])

    def test_fence_carries_no_level_across(self):
        """A fake deeper heading inside a fence must not create a jump
        for the first heading after the fence."""
        doc = self._run(
            "# A\n"
            "```markdown\n"
            "###### fake depth\n"
            "```\n"
            "## B\n"
        )
        self.assertEqual(doc.metadata["heading_issue_total"], 0)

    # ========== level_jump ==========

    def test_level_jump_triggered_and_boundary(self):
        """h1 -> h4 (skip 3) and h1 -> h3 (skip 2) are flagged; the exact
        one-level step h1 -> h2 is not, and jumping up any amount is
        always allowed."""
        self.assertEqual(self._kinds("# A\n#### B\n"), ["level_jump"])
        self.assertEqual(self._kinds("# A\n### B\n"), ["level_jump"])

        # boundary: skipping exactly one level is the normal nesting step
        self.assertEqual(self._kinds("# A\n## B\n### C\n## D\n# E\n"), [])

        # jumping back up any number of levels is fine
        self.assertEqual(self._kinds("### Deep Start\n## Up One\n# Top\n"),
                         [])

    def test_level_jump_detail_content(self):
        """The detail names both levels and the skip size (h1 -> h4 = 3)."""
        finding = self._run("# Guide\n#### Deep\n") \
            .metadata["heading_issues"][0]
        self.assertEqual(finding["kind"], "level_jump")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["text"], "Deep")
        self.assertEqual(finding["detail"],
                         "level jumps from 1 to 4 (skip 3)")

    def test_first_heading_never_level_jump(self):
        """The first heading has no predecessor, so even h6 first is not
        a level_jump (the dedicated first-heading check covers it)."""
        self.assertEqual(self._kinds("###### Only\n"), [])

    # ========== duplicate_heading ==========

    def test_duplicate_case_insensitive_with_occurrences(self):
        """Same casefolded title twice: one finding anchored at the first
        occurrence, listing every occurrence line."""
        finding = self._run("# Notes\nintro\n## notes\nmore\n# NOTES\n") \
            .metadata["heading_issues"][0]
        self.assertEqual(finding["kind"], "duplicate_heading")
        self.assertEqual(finding["line"], 1)
        self.assertEqual(finding["text"], "Notes")
        self.assertEqual(finding["detail"],
                         "appears 3 times at line(s) 1, 3, 5")

    def test_duplicate_ignores_level_and_whitespace(self):
        """Titles are compared casefolded and whitespace-collapsed,
        regardless of heading level."""
        self.assertEqual(self._kinds("# Notes\n## Notes\n"),
                         ["duplicate_heading"])
        self.assertEqual(self._kinds("## Setup Guide\n## Setup   Guide\n"),
                         ["duplicate_heading"])

    def test_unique_headings_not_flagged(self):
        """Distinct titles never trigger the duplicate check."""
        self.assertEqual(self._kinds("# Alpha\n## Beta\n## Gamma\n"), [])

    def test_empty_headings_excluded_from_duplicate_check(self):
        """Blank headings are reported by their own check only; two of
        them do not additionally count as a shared title."""
        doc = self._run("#\n##\n")
        self.assertEqual([f["kind"] for f in doc.metadata["heading_issues"]],
                         ["empty_heading", "empty_heading"])
        self.assertEqual(doc.metadata["heading_issue_counts"],
                         {"empty_heading": 2})

    # ========== empty_heading ==========

    def test_empty_heading_variants(self):
        """Bare markers, whitespace-only titles and bare closing
        sequences all leave no title text."""
        doc = self._run("#\n##   \n## ##\n### ###\n")
        self.assertEqual([f["kind"] for f in doc.metadata["heading_issues"]],
                         ["empty_heading"] * 4)
        self.assertEqual([f["line"] for f in doc.metadata["heading_issues"]],
                         [1, 2, 3, 4])
        self.assertEqual(doc.metadata["heading_issues"][0]["text"], "")
        self.assertEqual(doc.metadata["heading_issues"][0]["detail"],
                         "no text after the hashes")

    def test_non_empty_headings_not_flagged(self):
        """A heading with real text — including a title that merely ends
        in a hash — is never empty."""
        self.assertEqual(self._kinds("## Heading ##\n## Value#\n"), [])

    # ========== max_depth_exceeded ==========

    def test_max_depth_off_by_default(self):
        """max_level defaults to 6: a full one-step-at-a-time ladder down
        to h6 produces no finding of any kind."""
        self.assertEqual(
            self._kinds("# A\n## B\n### C\n#### D\n##### E\n###### F\n"),
            [])

    def test_max_depth_triggered_when_configured(self):
        """With max_level=3 the h4+ headings are flagged, h3 is not (the
        ladder itself descends one level at a time, so no level_jump
        mixes in)."""
        self.checker.max_level = 3
        doc = self._run("# A\n## B\n### C\n#### D\n##### E\n")
        findings = doc.metadata["heading_issues"]
        self.assertEqual([f["kind"] for f in findings],
                         ["max_depth_exceeded"] * 2)
        self.assertEqual([f["line"] for f in findings], [4, 5])
        self.assertEqual(findings[0]["detail"],
                         "level 4 exceeds max_level 3")

    def test_max_depth_via_yaml_config(self):
        """The tighter bound applies through the component configer too."""
        configer = self._create_configer({
            'name': 'heading_consistency_checker',
            'description': 'd', 'max_level': 2,
        })
        checker = HeadingConsistencyChecker()
        checker._initialize_by_component_configer(configer)
        doc = _doc("# A\n## B\n### C\n")
        checker.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["heading_issue_counts"],
                         {"max_depth_exceeded": 1})

    # ========== first_heading_not_h1 ==========

    def test_first_heading_check_off_by_default(self):
        """A document starting at h2 produces no finding by default."""
        self.assertEqual(self._kinds("## First\n### Sub\n"), [])

    def test_first_heading_check_when_enabled(self):
        """Enabled: an h2 start is reported with its line; an h1 start or
        a heading-less document is not."""
        self.checker.flag_first_not_h1 = True
        finding = self._run("intro\n## First\n### Sub\n") \
            .metadata["heading_issues"][0]
        self.assertEqual(finding["kind"], "first_heading_not_h1")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["text"], "First")
        self.assertEqual(finding["detail"],
                         "document starts at level 2 instead of 1")

        self.assertEqual(self._kinds("# Title\n## Sub\n"), [])

        doc = _doc("no headings at all")
        self.checker.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["heading_issues"], [])
        self.assertIsNone(doc.metadata["heading_score"])

    # ========== Score arithmetic (hand-verified) ==========

    def test_score_clean_document(self):
        """Zero findings on a real document: score 1.0, empty issues."""
        doc = self._run(CLEAN_DOC)
        self.assertEqual(doc.metadata["heading_issues"], [])
        self.assertEqual(doc.metadata["heading_issue_counts"], {})
        self.assertEqual(doc.metadata["heading_issue_total"], 0)
        self.assertEqual(doc.metadata["heading_score"], 1.0)

    def test_score_arithmetic_hand_verified(self):
        """1 finding -> 0.9, 3 -> 0.7, 10 -> 0.0 and 15 -> 0.0 (floor);
        empty headings give exact control of the finding count."""
        for total, expected in ((1, 0.9), (3, 0.7), (10, 0.0), (15, 0.0)):
            doc = self._run("#\n" * total)
            self.assertEqual(doc.metadata["heading_issue_total"], total)
            self.assertEqual(doc.metadata["heading_score"], expected,
                             f"total={total}")
            self.assertTrue(0.0 <= doc.metadata["heading_score"] <= 1.0)

    def test_score_integer_tenths_no_float_noise(self):
        """The score is computed in integer tenths: every value 0..10
        findings equals its exact decimal literal ('# Root' keeps the
        zero-finding case a real headed document)."""
        for total in range(11):
            doc = self._run("# Root\n" + "#\n" * total)
            self.assertEqual(doc.metadata["heading_issue_total"], total)
            self.assertEqual(doc.metadata["heading_score"],
                             round(1.0 - 0.1 * total, 1))

    def test_no_headings_score_is_null(self):
        """A document with no headings is not gradable: score None and
        empty findings — distinct from a checked-and-clean 1.0. Empty
        input lists pass through as empty."""
        doc = self._run("plain prose without any heading\nsecond line\n")
        self.assertIsNone(doc.metadata["heading_score"])
        self.assertEqual(doc.metadata["heading_issues"], [])
        self.assertEqual(doc.metadata["heading_issue_counts"], {})
        self.assertEqual(doc.metadata["heading_issue_total"], 0)

        self.assertEqual(self.checker.process_docs([], self.query), [])

    # ========== Findings cap and totals ==========

    def test_cap_limits_list_but_not_totals(self):
        """120 level jumps: the metadata list is capped at 100 while
        counts, total and score reflect all 120 findings."""
        text = "".join(f"# Chapter {i}\n#### Section {i}\n"
                       for i in range(120))
        doc = self._run(text)
        self.assertEqual(doc.metadata["heading_issue_total"], 120)
        self.assertEqual(len(doc.metadata["heading_issues"]), 100)
        self.assertEqual(doc.metadata["heading_issue_counts"],
                         {"level_jump": 120})
        self.assertEqual(doc.metadata["heading_score"], 0.0)

    def test_cap_configurable(self):
        """max_findings is a real knob: cap 5 keeps five entries and
        still reports the full total."""
        self.checker.max_findings = 5
        doc = self._run("#\n" * 8)
        self.assertEqual(len(doc.metadata["heading_issues"]), 5)
        self.assertEqual(doc.metadata["heading_issue_total"], 8)

    # ========== Combined document (hand-verified) ==========

    def test_combined_document_counts_and_order(self):
        """COMBINED_DOC yields exactly one duplicate, one empty and two
        level jumps, sorted by line, with score 1.0 - 0.4 = 0.6."""
        doc = self._run(COMBINED_DOC)
        findings = doc.metadata["heading_issues"]
        self.assertEqual([(f["kind"], f["line"]) for f in findings], [
            ("level_jump", 2),
            ("duplicate_heading", 3),
            ("empty_heading", 5),
            ("level_jump", 6),
        ])
        self.assertEqual(findings[1]["text"], "Setup")
        self.assertEqual(findings[1]["detail"],
                         "appears 2 times at line(s) 3, 4")
        self.assertEqual(doc.metadata["heading_issue_counts"],
                         {"level_jump": 2, "duplicate_heading": 1,
                          "empty_heading": 1})
        self.assertEqual(doc.metadata["heading_issue_total"], 4)
        self.assertEqual(doc.metadata["heading_score"], 0.6)

    def test_finding_schema(self):
        """Every finding carries exactly {kind, line, text, detail} with
        the documented types."""
        for finding in self._run(COMBINED_DOC).metadata["heading_issues"]:
            self.assertEqual(set(finding), {"kind", "line", "text", "detail"})
            self.assertIsInstance(finding["kind"], str)
            self.assertIsInstance(finding["line"], int)
            self.assertIsInstance(finding["text"], str)
            self.assertIsInstance(finding["detail"], str)

    # ========== Pipeline-shape tests ==========

    def test_documents_pass_through_unchanged(self):
        """The checker validates, never filters: same objects, same
        order, same text and id — only metadata gains the stamps."""
        docs = [_doc(COMBINED_DOC, source="docs"),
                _doc("nothing here")]
        result = self.checker.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], docs[0])
        self.assertIs(result[1], docs[1])
        self.assertEqual(result[0].text, COMBINED_DOC)
        self.assertIsNotNone(result[0].id)
        self.assertEqual(result[1].text, "nothing here")

    def test_documents_analyzed_independently(self):
        """Heading-level tracking never leaks across documents: the h4 in
        the first document does not make the second document's h3 start
        look like a jump up or down."""
        docs = [_doc("# A\n#### B\n"), _doc("### Orphan\n#### Child\n")]
        result = self.checker.process_docs(docs, self.query)
        self.assertEqual(result[0].metadata["heading_issue_total"], 1)
        self.assertEqual(result[1].metadata["heading_issue_total"], 0)
        self.assertEqual(result[1].metadata["heading_score"], 1.0)

    def test_metadata_not_corrupted_and_copied(self):
        """Pre-existing metadata survives, and stamps write through a
        copied mapping — the caller's original dict is never mutated in
        place."""
        doc = _doc(COMBINED_DOC, source="export", rank=2)
        original_meta = doc.metadata
        self.checker.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["source"], "export")
        self.assertEqual(doc.metadata["rank"], 2)
        self.assertIsNot(doc.metadata, original_meta)
        for key in ("heading_issues", "heading_issue_counts",
                    "heading_issue_total", "heading_score"):
            self.assertNotIn(key, original_meta)

    def test_disabled_keys_stamp_nothing(self):
        """Empty key names disable every stamp; existing metadata stays
        exactly as it was."""
        for attr in ("issues_key", "counts_key", "total_key", "score_key"):
            setattr(self.checker, attr, "")
        doc = _doc(COMBINED_DOC, source="export")
        self.checker.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"source": "export"})

    def test_custom_metadata_keys(self):
        """Configured key names are honored end to end."""
        self.checker.issues_key = "outline_problems"
        self.checker.score_key = "outline_score"
        doc = _doc("# A\n#### B\n")
        self.checker.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["outline_problems"]), 1)
        self.assertEqual(doc.metadata["outline_score"], 0.9)

    def test_deterministic_across_runs_and_instances(self):
        """Identical inputs produce identical metadata on repeated runs
        and across fresh checker instances (no hash-order dependence)."""
        first = self._run(COMBINED_DOC)
        snapshot = copy.deepcopy(first.metadata)
        for _ in range(3):
            again = HeadingConsistencyChecker() \
                .process_docs([_doc(COMBINED_DOC)], self.query)[0]
            self.assertEqual(again.metadata, snapshot)

    def test_none_and_blank_text_documents(self):
        """Blank text behaves as a document without headings: score
        None, no findings, no crash. (Document rejects text=None at
        construction, so the None guard is covered at the parser.)"""
        self.assertEqual(
            HeadingConsistencyChecker._parse_headings(None), [])
        for text in ("", "   \n\t\n"):
            doc = _doc(text)
            self.checker.process_docs([doc], self.query)
            self.assertIsNone(doc.metadata["heading_score"])
            self.assertEqual(doc.metadata["heading_issues"], [])


if __name__ == '__main__':
    unittest.main()
