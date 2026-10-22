# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_outline_extractor.py

import os
import unittest

import yaml

from agentuniverse.agent.action.knowledge.doc_processor.outline_extractor import OutlineExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# All six ATX levels, followed by lines that must NOT be headings.
ATX_DOC = (
    "# Title\n"
    "\n"
    "## Intro\n"
    "\n"
    "### Methods\n"
    "\n"
    "#### Details\n"
    "\n"
    "##### Notes\n"
    "\n"
    "###### Appendix\n"
    "\n"
    "####### Seven hashes is not a heading\n"
    "\n"
    "#NoSpaceNotHeading\n"
    "\n"
    "    # Four-space indent is not a heading\n"
    "\n"
    "#\n"
)

# Setext headings plus delimiters that must stay inert.
SETEXT_DOC = (
    "Main Title\n"
    "==========\n"
    "\n"
    "Section One\n"
    "-----------\n"
    "\n"
    "---\n"
    "\n"
    "A plain closing paragraph\n"
)

# Headings inside fenced code blocks must be ignored, no matter whether
# the fence uses backticks (with info string) or tildes.
FENCE_DOC = (
    "# Real Title\n"
    "\n"
    "```python\n"
    "# comment heading inside fence\n"
    "## another inside\n"
    "```\n"
    "\n"
    "~~~\n"
    "# tilde fenced\n"
    "~~~\n"
    "\n"
    "## After Fences\n"
)

# A four-backtick fence is only closed by four or more backticks, so the
# inner three-backtick line is content, not a closer.
LONG_FENCE_DOC = (
    "# Start\n"
    "````\n"
    "```\n"
    "# quoted heading\n"
    "````\n"
    "# End\n"
)

# Arabic numbered sections: trailing dot optional, depth = dot depth.
NUMBERED_DOC = (
    "1. Introduction\n"
    "1.1 Background\n"
    "1.1.1 Scope\n"
    "2 Methods\n"
    "3. Results\n"
    "1.1. Details\n"
)

# Chinese numbered sections. First-occurrence depth assignment:
# chapter -> 1, dun -> 2, paren -> 3.
CJK_DOC = (
    "第一章 总则\n"
    "一、总体要求\n"
    "（一）主要目标\n"
    "二、保障措施\n"
    "（二）次要目标\n"
    "第二章 附则\n"
    "(三)半角括号\n"
)

# A Markdown / Arabic / CJK mix: every heading keeps its own rule.
MIXED_DOC = (
    "# Guide\n"
    "## Part One\n"
    "1. Setup\n"
    "1.1 Install\n"
    "2. Usage\n"
    "## Part Two\n"
    "一、说明\n"
)

# Prose that must not be mistaken for headings: sentence starting with a
# decimal number, an over-long numbered line and an indented list item.
PROSE_DOC = (
    "In 2024 the team shipped twice.\n"
    "1.5 million units were sold.\n"
    + "4. " + "word " * 30 + "\n"
    + "    1. Indented list items are not headings\n"
    + "See section 2.3 for details\n"
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _summary(outline):
    """Reduce an outline to comparable (level, number, text) tuples."""
    return [(h["level"], h["number"], h["text"]) for h in outline]


class TestOutlineExtractor(unittest.TestCase):
    """Comprehensive test suite for OutlineExtractor."""

    def setUp(self):
        self.extractor = OutlineExtractor()
        self.query = Query(query_str="outline")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _outline_of(self, text, extractor=None):
        """Run the scan on a bare text and return the outline list."""
        return (extractor or self.extractor)._scan(text)

    # ========== Configuration tests ==========

    def test_default_configuration(self):
        """Defaults: min_headings 1, stamping under the 'outline' key."""
        extractor = OutlineExtractor()
        self.assertEqual(extractor.min_headings, 1)
        self.assertEqual(extractor.outline_key, "outline")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'outline_extractor',
            'description': 'outline extractor',
            'min_headings': 4,
            'outline_key': 'headings',
        })
        extractor = OutlineExtractor()
        extractor._initialize_by_component_configer(configer)
        self.assertEqual(extractor.min_headings, 4)
        self.assertEqual(extractor.outline_key, "headings")
        self.assertEqual(extractor.name, "outline_extractor")

    def test_invalid_min_headings_raises(self):
        """min_headings must be an integer >= 1; zero, negatives, floats,
        booleans and strings all fail at load time."""
        for bad in (0, -1, 1.5, True, "3"):
            configer = self._create_configer({
                'name': 'f', 'description': 'd', 'min_headings': bad,
            })
            with self.assertRaises(ValueError):
                OutlineExtractor()._initialize_by_component_configer(configer)

    def test_invalid_outline_key_raises(self):
        """outline_key must be a string."""
        configer = self._create_configer({
            'name': 'f', 'description': 'd', 'outline_key': 123,
        })
        with self.assertRaises(ValueError):
            OutlineExtractor()._initialize_by_component_configer(configer)

    def test_shipped_yaml_definition_wiring(self):
        """The shipped yaml points at this module and class."""
        repo_root = os.path.abspath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', '..', '..', '..', '..', '..'))
        yaml_path = os.path.join(
            repo_root, 'agentuniverse', 'agent', 'action', 'knowledge',
            'doc_processor', 'outline_extractor.yaml')
        with open(yaml_path, 'r', encoding='utf-8') as fh:
            config = yaml.safe_load(fh)
        self.assertEqual(config['metadata']['type'], 'DOC_PROCESSOR')
        self.assertEqual(config['metadata']['class'], 'OutlineExtractor')
        self.assertEqual(
            config['metadata']['module'],
            'agentuniverse.agent.action.knowledge.doc_processor'
            '.outline_extractor')
        self.assertEqual(config['min_headings'], 1)
        self.assertEqual(config['outline_key'], 'outline')

    # ========== ATX tests ==========

    def test_atx_levels_and_order(self):
        """ATX headings give levels 1..6 in document order; malformed
        lines (seven hashes, missing blank, four-space indent, bare hash)
        are ignored."""
        outline = self._outline_of(ATX_DOC)
        self.assertEqual(_summary(outline), [
            (1, None, "Title"),
            (2, None, "Intro"),
            (3, None, "Methods"),
            (4, None, "Details"),
            (5, None, "Notes"),
            (6, None, "Appendix"),
        ])

    def test_atx_span_precision(self):
        """An ATX span points exactly at the title inside the text."""
        outline = self._outline_of("# Title")
        self.assertEqual(outline[0]["span"], [2, 7])
        text = ATX_DOC
        for heading in self._outline_of(text):
            start, end = heading["span"]
            self.assertEqual(text[start:end], heading["text"])

    def test_atx_closing_hash_run_stripped(self):
        """A closing hash run ('## Title ##') is stripped from the title;
        a hashes-only title ('### ###') is an empty heading, not an
        entry."""
        outline = self._outline_of("## Title ##\n\n### ###\n")
        self.assertEqual(_summary(outline), [(2, None, "Title")])

    def test_atx_tab_separator_and_long_titles(self):
        """Tabs separate marker from title; ATX titles are exempt from
        the unmarked-form length guard."""
        outline = self._outline_of("#\tTabbed\n")
        self.assertEqual(_summary(outline), [(1, None, "Tabbed")])
        long_title = ("long " * 40).rstrip()  # 199 chars, well over 120
        outline = self._outline_of("# " + long_title + "\n")
        self.assertEqual(_summary(outline), [(1, None, long_title)])

    def test_atx_heading_not_converted_by_following_underline(self):
        """An ATX heading is a complete block: a following '===' line is
        plain text and must not turn it into a setext heading."""
        outline = self._outline_of("## Title\n=====\n")
        self.assertEqual(_summary(outline), [(2, None, "Title")])

    # ========== Fenced code block tests ==========

    def test_fenced_code_blocks_are_skipped(self):
        """Headings inside ``` and ~~~ fences never match, while headings
        before and after the fences do."""
        outline = self._outline_of(FENCE_DOC)
        self.assertEqual(_summary(outline), [
            (1, None, "Real Title"),
            (2, None, "After Fences"),
        ])

    def test_longer_fence_not_closed_by_shorter_marker(self):
        """A four-backtick fence is not closed by a three-backtick line;
        content in between (including that line) stays inert."""
        outline = self._outline_of(LONG_FENCE_DOC)
        self.assertEqual(_summary(outline), [
            (1, None, "Start"),
            (1, None, "End"),
        ])

    # ========== Setext tests ==========

    def test_setext_levels_and_spans(self):
        """'===' underlines make level 1, '---' level 2; spans point at
        the title line, not the underline."""
        outline = self._outline_of(SETEXT_DOC)
        self.assertEqual(_summary(outline), [
            (1, None, "Main Title"),
            (2, None, "Section One"),
        ])
        self.assertEqual(outline[0]["span"], [0, 10])
        text = SETEXT_DOC
        for heading in outline:
            start, end = heading["span"]
            self.assertEqual(text[start:end], heading["text"])

    def test_underline_without_title_line_is_inert(self):
        """A '---' at document start or after a blank line is a thematic
        break / front-matter delimiter, never a heading."""
        outline = self._outline_of("---\nkey: value\n\n---\nplain text\n"
                                   "\n---\n")
        self.assertEqual(_summary(outline), [])

    def test_setext_underline_replaces_numbered_heading(self):
        """A '===' underline claims the previous line: a numbered heading
        recorded from that line is replaced by one setext entry whose
        text is the whole underlined line."""
        outline = self._outline_of("1. Intro\n========\n")
        self.assertEqual(_summary(outline), [(1, None, "1. Intro")])

    # ========== Arabic numbered tests ==========

    def test_numbered_depths_and_numbers(self):
        """Dot depth gives the level; the trailing dot is optional and
        the marker is recorded without it."""
        outline = self._outline_of(NUMBERED_DOC)
        self.assertEqual(_summary(outline), [
            (1, "1", "Introduction"),
            (2, "1.1", "Background"),
            (3, "1.1.1", "Scope"),
            (1, "2", "Methods"),
            (1, "3", "Results"),
            (2, "1.1", "Details"),
        ])

    def test_numbered_span_precision(self):
        """A numbered span points exactly at the title text."""
        text = "1. Introduction\n"
        outline = self._outline_of(text)
        self.assertEqual(outline[0]["span"], [3, 15])
        self.assertEqual(text[3:15], "Introduction")

    def test_prose_is_not_mistaken_for_headings(self):
        """Decimal sentence starts, over-long numbered lines and indented
        list items produce no headings at all."""
        self.assertEqual(self._outline_of(PROSE_DOC), [])

    # ========== CJK numbered tests ==========

    def test_cjk_forms_and_first_occurrence_depth(self):
        """Chapter/dun/paren forms are recognized with their markers as
        numbers; depths follow first occurrence: 1, 2, 3."""
        outline = self._outline_of(CJK_DOC)
        self.assertEqual(_summary(outline), [
            (1, "第一章", "总则"),
            (2, "一、", "总体要求"),
            (3, "（一）", "主要目标"),
            (2, "二、", "保障措施"),
            (3, "（二）", "次要目标"),
            (1, "第二章", "附则"),
            (3, "(三)", "半角括号"),
        ])

    def test_cjk_bare_chapter_marker(self):
        """A bare '第一章' line is a heading whose text is the marker;
        a bare '一、' without title text is skipped."""
        outline = self._outline_of("第一章\n正文内容\n\n一、\n正文\n")
        self.assertEqual(_summary(outline), [(1, "第一章", "第一章")])
        self.assertEqual(outline[0]["span"], [0, 3])

    def test_cjk_fullwidth_space_separator(self):
        """The fullwidth space (U+3000) separates marker and title."""
        outline = self._outline_of("第一章　总则\n")
        self.assertEqual(_summary(outline), [(1, "第一章", "总则")])

    def test_cjk_paren_first_when_document_opens_with_it(self):
        """The first CJK form encountered gets level 1 even when it is
        the paren form."""
        outline = self._outline_of("（一）计划\n（二）执行\n一、附注\n")
        self.assertEqual(_summary(outline), [
            (1, "（一）", "计划"),
            (1, "（二）", "执行"),
            (2, "一、", "附注"),
        ])

    def test_cjk_span_precision(self):
        """CJK spans point exactly at the title (or the bare marker)."""
        text = "第一章 总则\n"
        outline = self._outline_of(text)
        self.assertEqual(outline[0]["span"], [4, 6])
        self.assertEqual(text[4:6], "总则")

    # ========== Mixed documents ==========

    def test_mixed_document_keeps_each_rule(self):
        """ATX levels, dot depths and CJK first-occurrence depths coexist
        in one document without disturbing each other."""
        outline = self._outline_of(MIXED_DOC)
        self.assertEqual(_summary(outline), [
            (1, None, "Guide"),
            (2, None, "Part One"),
            (1, "1", "Setup"),
            (2, "1.1", "Install"),
            (1, "2", "Usage"),
            (2, None, "Part Two"),
            (1, "一、", "说明"),
        ])

    def test_mixed_document_span_invariant(self):
        """For every entry of a rich document text[start:end] == text."""
        for text in (ATX_DOC, SETEXT_DOC, FENCE_DOC, LONG_FENCE_DOC,
                     NUMBERED_DOC, CJK_DOC, MIXED_DOC):
            for heading in self._outline_of(text):
                start, end = heading["span"]
                self.assertEqual(
                    text[start:end], heading["text"],
                    msg=f"span mismatch for {heading!r} in {text!r}")

    # ========== Metadata stamping ==========

    def test_metadata_stamp_contents(self):
        """A rich document gets outline, section_count and max_depth."""
        doc = _doc(CJK_DOC)
        result = self.extractor.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        meta = doc.metadata
        self.assertEqual(len(meta["outline"]), 7)
        self.assertEqual(meta["section_count"], 7)
        self.assertEqual(meta["max_depth"], 3)
        self.assertNotIn("outline_note", meta)
        for entry in meta["outline"]:
            self.assertEqual(set(entry), {"level", "text", "span", "number"})

    def test_mixed_metadata_max_depth(self):
        """max_depth spans all forms (ATX depth 2 here)."""
        doc = _doc(MIXED_DOC)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["section_count"], 7)
        self.assertEqual(doc.metadata["max_depth"], 2)

    def test_existing_metadata_preserved_and_copy_on_write(self):
        """Pre-existing metadata survives; the mapping is replaced by a
        copy, never mutated in place."""
        shared = {"source": "wiki", "lang": "zh"}
        doc = Document(text=CJK_DOC, metadata=shared)
        self.extractor.process_docs([doc], self.query)
        self.assertIsNot(doc.metadata, shared)
        self.assertNotIn("outline", shared)
        self.assertEqual(doc.metadata["source"], "wiki")
        self.assertEqual(doc.metadata["lang"], "zh")
        self.assertIn("outline", doc.metadata)

    def test_text_and_id_untouched(self):
        """Text and id are never modified by stamping."""
        doc = _doc(NUMBERED_DOC)
        before_text, before_id = doc.text, doc.id
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.text, before_text)
        self.assertEqual(doc.id, before_id)

    def test_batch_order_and_multiple_docs(self):
        """The same list and document objects come back in the same
        order, each stamped with its own outline."""
        doc_a = _doc("# A\n")
        doc_b = _doc("no headings here\n")
        doc_c = _doc("1. Only\n")
        docs = [doc_a, doc_b, doc_c]
        result = self.extractor.process_docs(docs, self.query)
        self.assertIs(result, docs)
        self.assertEqual([d.id for d in result], [d.id for d in docs])
        self.assertEqual(result[0].metadata["section_count"], 1)
        self.assertEqual(result[1].metadata["section_count"], 0)
        self.assertEqual(result[2].metadata["section_count"], 1)

    def test_empty_batch(self):
        """An empty batch processes to an empty list."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])

    # ========== No-heading documents ==========

    def test_no_heading_document_gets_empty_outline_and_note(self):
        """0-heading documents are stamped with an empty outline, zero
        counters and a note, even when min_headings is higher."""
        extractor = OutlineExtractor()
        extractor.min_headings = 5
        doc = _doc(PROSE_DOC, source="log")
        extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["outline"], [])
        self.assertEqual(doc.metadata["section_count"], 0)
        self.assertEqual(doc.metadata["max_depth"], 0)
        self.assertEqual(doc.metadata["outline_note"],
                         "no headings detected")
        self.assertEqual(doc.metadata["source"], "log")

    def test_empty_and_default_text(self):
        """Empty text and the default (unset) text behave like 0-heading
        documents. (Document(text=None) cannot even be constructed — the
        framework validator rejects it — so None never reaches the
        processor; the scan still guards it defensively.)"""
        for doc in (_doc(""), Document()):
            self.extractor.process_docs([doc], self.query)
            self.assertEqual(doc.metadata["outline"], [])
            self.assertEqual(doc.metadata["section_count"], 0)
            self.assertEqual(doc.metadata["max_depth"], 0)
            self.assertIn("outline_note", doc.metadata)
        self.assertEqual(self.extractor._scan(None), [])

    # ========== min_headings option ==========

    def test_min_headings_threshold(self):
        """Documents with 1..min-1 headings are left completely
        untouched; at min headings the outline is stamped."""
        two = "# One\n## Two\n"
        extractor = OutlineExtractor()
        extractor.min_headings = 3
        doc = _doc(two, source="keep")
        extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"source": "keep"})

        extractor.min_headings = 2
        doc = _doc(two, source="keep")
        extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["section_count"], 2)
        self.assertEqual(doc.metadata["source"], "keep")

    def test_disabled_outline_key_stamps_nothing(self):
        """An empty outline_key disables all stamping, even for
        0-heading documents."""
        extractor = OutlineExtractor()
        extractor.outline_key = ""
        doc_plain = _doc("# Heading\n")
        doc_empty = _doc("nothing\n")
        extractor.process_docs([doc_plain, doc_empty], self.query)
        self.assertIsNone(doc_plain.metadata)
        self.assertIsNone(doc_empty.metadata)

    def test_custom_outline_key_uses_derived_note_key(self):
        """A custom outline key moves the note to '<key>_note'."""
        extractor = OutlineExtractor()
        extractor.outline_key = "headings"
        doc = _doc("no structure\n")
        extractor.process_docs([doc], self.query)
        self.assertIn("headings", doc.metadata)
        self.assertIn("headings_note", doc.metadata)
        self.assertNotIn("outline_note", doc.metadata)

    # ========== Determinism ==========

    def test_determinism_across_runs_and_instances(self):
        """Repeated runs and separate instances produce identical
        outlines for the same text."""
        first = self._outline_of(MIXED_DOC)
        second = self._outline_of(MIXED_DOC)
        self.assertEqual(first, second)
        other = OutlineExtractor()
        self.assertEqual(other._scan(MIXED_DOC), first)

        doc_one, doc_two = _doc(MIXED_DOC), _doc(MIXED_DOC)
        self.extractor.process_docs([doc_one], self.query)
        self.extractor.process_docs([doc_two], self.query)
        self.assertEqual(doc_one.metadata["outline"],
                         doc_two.metadata["outline"])


if __name__ == "__main__":
    unittest.main()
