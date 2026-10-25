# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_qa_pair_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.qa_pair_extractor import QAPairExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Prefix format, English: two pairs, the first with a multi-line answer
# spanning an interior blank line region.
EN_PREFIX_FAQ = (
    "Q: What is agentUniverse?\n"
    "A: agentUniverse is an open-source framework\n"
    "for building agent applications, developed by Ant Group.\n"
    "\n"
    "Q: How do I install it?\n"
    "A: Run pip install agentuniverse and wait for the\n"
    "installation to finish."
)

EN_PREFIX_LONG_FAQ = (
    "Question: What is agentUniverse?\n"
    "Answer: An open-source agent framework."
)

EN_PREFIX_NUMBERED_FAQ = (
    "Q1: What is agentUniverse?\n"
    "A1: An open-source agent framework."
)

# Prefix format, Chinese: full-width colons plus the longer 问题/回答
# marker pair, separated by a blank line.
ZH_PREFIX_FAQ = (
    "问：什么是 agentUniverse？\n"
    "答：agentUniverse 是一个开源的智能体应用开发框架。\n"
    "\n"
    "问题：如何安装？\n"
    "回答：执行 pip install agentuniverse 即可完成安装。"
)

# Heading format: ##/### sections, English and Chinese.
EN_HEADING_FAQ = (
    "## What is agentUniverse?\n"
    "An open-source framework for building agent applications.\n"
    "\n"
    "### How do I install it?\n"
    "Run pip install agentuniverse."
)

ZH_HEADING_FAQ = (
    "## 什么是 agentUniverse？\n"
    "agentUniverse 是一个开源的智能体应用开发框架。\n"
    "\n"
    "### 如何安装它？\n"
    "执行 pip install agentuniverse。"
)

BOLD_FAQ = (
    "**What is agentUniverse?**\n"
    "An open-source framework for agent applications.\n"
    "\n"
    "**How do I install it?**\n"
    "Run pip install agentuniverse."
)

# Numbered format with inline separators: em-dash, ASCII double hyphen
# and a plain colon; Chinese uses 、 numbering and the double em-dash.
EN_NUMBERED_INLINE = (
    "1. What is agentUniverse? — An open-source agent framework.\n"
    "2. How do I install it? -- Run pip install agentuniverse.\n"
    "3. Where are the docs? : On the documentation site."
)

ZH_NUMBERED_INLINE = (
    "1、什么是 agentUniverse？—— 一个开源的智能体应用开发框架。\n"
    "2、如何安装？——执行 pip install agentuniverse。"
)

# Numbered format with the answer on the following lines.
EN_NUMBERED_NEXT_LINE = (
    "1. What is agentUniverse?\n"
    "An open-source agent framework with components\n"
    "for planning, action and knowledge.\n"
    "\n"
    "2. How do I install it?\n"
    "Run pip install agentuniverse."
)

# A document mixing all three formats (plus an intro paragraph that must
# not produce a pair); the ground-truth pairs below pin the exact
# extraction order and text.
MIXED_FAQ = (
    "Frequently asked questions about agentUniverse.\n"
    "\n"
    "## What is agentUniverse?\n"
    "An open-source framework for building agent applications.\n"
    "\n"
    "Q: Is it free to use?\n"
    "A: Yes, it is released under the Apache-2.0 license.\n"
    "\n"
    "1. How do I install it? — Run pip install agentuniverse.\n"
    "\n"
    "**Where can I find the docs?**\n"
    "On the official documentation site."
)

MIXED_FAQ_PAIRS = [
    ("What is agentUniverse?",
     "An open-source framework for building agent applications."),
    ("Is it free to use?",
     "Yes, it is released under the Apache-2.0 license."),
    ("How do I install it?", "Run pip install agentuniverse."),
    ("Where can I find the docs?", "On the official documentation site."),
]

# Plain prose without any FAQ structure.
NO_FAQ_PROSE = (
    "This is a plain paragraph without any FAQ structure.\n"
    "It just explains something in two lines."
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _pairs(result):
    """Reduce processed documents to their (question, answer) metadata."""
    return [(d.metadata["question"], d.metadata["answer"]) for d in result]


class TestQAPairExtractor(unittest.TestCase):
    """Comprehensive test suite for QAPairExtractor."""

    def setUp(self):
        self.extractor = QAPairExtractor()
        self.query = Query(query_str="faq")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: all three formats, min answer 1 char, unlimited max
        answer, 100 pairs, replace source."""
        e = QAPairExtractor()
        self.assertEqual(e.formats, ["prefix", "numbered", "heading"])
        self.assertEqual(e.min_answer_chars, 1)
        self.assertEqual(e.max_answer_chars, 0)
        self.assertEqual(e.max_pairs, 100)
        self.assertFalse(e.keep_source)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization, and a
        duplicate format entry is collapsed."""
        configer = self._create_configer({
            'name': 'qa_pair_extractor',
            'description': 'qa pair extractor',
            'formats': ['prefix', 'heading', 'prefix'],
            'min_answer_chars': 2,
            'max_answer_chars': 500,
            'max_pairs': 10,
            'keep_source': True,
        })
        e = QAPairExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.formats, ["prefix", "heading"])
        self.assertEqual(e.min_answer_chars, 2)
        self.assertEqual(e.max_answer_chars, 500)
        self.assertEqual(e.max_pairs, 10)
        self.assertTrue(e.keep_source)
        self.assertEqual(e.name, "qa_pair_extractor")

    def test_invalid_configuration_raises(self):
        """Bad format lists, non-integer or out-of-range bounds, inverted
        min/max and non-positive max_pairs all fail at load time."""
        base = {
            'name': 'e', 'description': 'd',
            'formats': ['prefix'], 'min_answer_chars': 1,
            'max_answer_chars': 0, 'max_pairs': 5, 'keep_source': False,
        }
        for key, value in (
            ('formats', 'prefix'),
            ('formats', []),
            ('formats', ['bogus']),
            ('formats', 7),
            ('min_answer_chars', -1),
            ('min_answer_chars', 1.5),
            ('min_answer_chars', True),
            ('max_answer_chars', -1),
            ('max_answer_chars', 2.5),
            ('max_answer_chars', True),
            ('max_pairs', 0),
            ('max_pairs', -3),
            ('max_pairs', 1.5),
            ('max_pairs', True),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                QAPairExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_min_greater_than_max_raises_only_when_max_set(self):
        """min > max is rejected while max is a real limit, but any min
        is fine next to the unlimited default max of 0."""
        with self.assertRaises(ValueError):
            QAPairExtractor()._initialize_by_component_configer(
                self._create_configer({'name': 'e', 'description': 'd',
                                       'min_answer_chars': 10,
                                       'max_answer_chars': 5}))
        QAPairExtractor()._initialize_by_component_configer(
            self._create_configer({'name': 'e', 'description': 'd',
                                   'min_answer_chars': 10,
                                   'max_answer_chars': 0}))

    # ========== Empty / passthrough tests ==========

    def test_empty_input_returns_empty(self):
        """An empty batch produces an empty batch."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])

    def test_empty_text_passthrough(self):
        """Documents with empty text pass through unchanged."""
        doc = _doc("")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)

    def test_no_qa_prose_passthrough(self):
        """Prose without FAQ structure passes through unchanged, both
        with keep_source false (default) and true."""
        doc = _doc(NO_FAQ_PROSE, lang="en")
        for keep_source in (False, True):
            self.extractor.keep_source = keep_source
            result = self.extractor.process_docs([doc], self.query)
            self.assertEqual(len(result), 1)
            self.assertIs(result[0], doc)
            self.assertEqual(result[0].text, NO_FAQ_PROSE)

    # ========== Prefix format tests ==========

    def test_prefix_english(self):
        """Q:/A: blocks yield exact ground-truth pairs, keeping the
        multi-line answer intact."""
        result = self.extractor.process_docs([_doc(EN_PREFIX_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("What is agentUniverse?",
             "agentUniverse is an open-source framework\n"
             "for building agent applications, developed by Ant Group."),
            ("How do I install it?",
             "Run pip install agentuniverse and wait for the\n"
             "installation to finish."),
        ])

    def test_prefix_english_long_markers(self):
        """Question:/Answer: markers are recognized as well."""
        result = self.extractor.process_docs([_doc(EN_PREFIX_LONG_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result),
                         [("What is agentUniverse?",
                           "An open-source agent framework.")])

    def test_prefix_numbered_markers(self):
        """Q1:/A1: item-numbered markers are recognized."""
        result = self.extractor.process_docs([_doc(EN_PREFIX_NUMBERED_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result),
                         [("What is agentUniverse?",
                           "An open-source agent framework.")])

    def test_prefix_chinese(self):
        """问：/答： and 问题：/回答： markers with full-width colons yield
        exact ground-truth pairs."""
        result = self.extractor.process_docs([_doc(ZH_PREFIX_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("什么是 agentUniverse？",
             "agentUniverse 是一个开源的智能体应用开发框架。"),
            ("如何安装？", "执行 pip install agentuniverse 即可完成安装。"),
        ])

    def test_prefix_orphan_question_skipped(self):
        """A question marker without a following answer marker produces
        no pair, and later complete blocks still extract."""
        text = ("Q: orphan question without answer\n"
                "plain line\n"
                "Q: real question?\n"
                "A: real answer.")
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(_pairs(result), [("real question?", "real answer.")])

    # ========== Heading format tests ==========

    def test_heading_english(self):
        """##/### headings followed by answer paragraphs extract in
        document order."""
        result = self.extractor.process_docs([_doc(EN_HEADING_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("What is agentUniverse?",
             "An open-source framework for building agent applications."),
            ("How do I install it?", "Run pip install agentuniverse."),
        ])

    def test_heading_chinese(self):
        """Chinese markdown headings ending in ？ extract the same way."""
        result = self.extractor.process_docs([_doc(ZH_HEADING_FAQ)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("什么是 agentUniverse？",
             "agentUniverse 是一个开源的智能体应用开发框架。"),
            ("如何安装它？", "执行 pip install agentuniverse。"),
        ])

    def test_bold_questions(self):
        """Standalone **bold** lines act as question markers."""
        result = self.extractor.process_docs([_doc(BOLD_FAQ)], self.query)
        self.assertEqual(_pairs(result), [
            ("What is agentUniverse?",
             "An open-source framework for agent applications."),
            ("How do I install it?", "Run pip install agentuniverse."),
        ])

    def test_heading_without_answer_skipped(self):
        """Consecutive headings yield no pair for the answer-less one."""
        text = ("## Question without answer\n"
                "## Real question?\n"
                "Its answer.")
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(_pairs(result), [("Real question?", "Its answer.")])

    # ========== Numbered format tests ==========

    def test_numbered_inline_separators(self):
        """Em-dash, ASCII double hyphen and colon separators all split
        question from answer on the same line."""
        result = self.extractor.process_docs([_doc(EN_NUMBERED_INLINE)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("What is agentUniverse?", "An open-source agent framework."),
            ("How do I install it?", "Run pip install agentuniverse."),
            ("Where are the docs?", "On the documentation site."),
        ])

    def test_numbered_inline_chinese(self):
        """Chinese 、 numbering and the double em-dash —— separator work,
        including without a space after the separator."""
        result = self.extractor.process_docs([_doc(ZH_NUMBERED_INLINE)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("什么是 agentUniverse？",
             "一个开源的智能体应用开发框架。"),
            ("如何安装？", "执行 pip install agentuniverse。"),
        ])

    def test_numbered_answer_on_next_lines(self):
        """A numbered question with the answer on the following lines
        keeps the multi-line answer and stops before the next item."""
        result = self.extractor.process_docs([_doc(EN_NUMBERED_NEXT_LINE)],
                                             self.query)
        self.assertEqual(_pairs(result), [
            ("What is agentUniverse?",
             "An open-source agent framework with components\n"
             "for planning, action and knowledge."),
            ("How do I install it?", "Run pip install agentuniverse."),
        ])

    def test_numbered_plain_statements_ignored(self):
        """Numbered items that are not questions produce no pairs."""
        text = ("1. first step of a process\n"
                "2. second step of a process")
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, text)

    # ========== Mixed document / determinism tests ==========

    def test_mixed_document_ground_truth(self):
        """A document combining heading, prefix, numbered and bold blocks
        extracts exactly the pinned pairs in document order."""
        result = self.extractor.process_docs([_doc(MIXED_FAQ)], self.query)
        self.assertEqual(_pairs(result), MIXED_FAQ_PAIRS)

    def test_mixed_extraction_is_deterministic(self):
        """Repeated runs on the same input return identical output."""
        first = self.extractor.process_docs([_doc(MIXED_FAQ)], self.query)
        second = QAPairExtractor().process_docs([_doc(MIXED_FAQ)],
                                                self.query)
        self.assertEqual([(d.text, d.metadata) for d in first],
                         [(d.text, d.metadata) for d in second])

    def test_prefix_inside_heading_section_wins(self):
        """A heading section that begins with Q:/A: lines yields the
        explicit prefix pair, not an empty heading pair."""
        text = ("## What is agentUniverse?\n"
                "Q: nested question\n"
                "A: nested answer")
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(_pairs(result),
                         [("nested question", "nested answer")])

    # ========== Output document tests ==========

    def test_pair_document_text_and_metadata(self):
        """Pair documents read 'Q: {q}\\nA: {a}' and carry exactly the
        four documented metadata keys with correct values."""
        doc = _doc(EN_PREFIX_LONG_FAQ)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        pair = result[0]
        self.assertEqual(pair.text,
                         "Q: What is agentUniverse?\n"
                         "A: An open-source agent framework.")
        self.assertEqual(pair.metadata, {
            "pair_index": 0,
            "question": "What is agentUniverse?",
            "answer": "An open-source agent framework.",
            "source_doc_id": doc.id,
        })

    def test_pair_indices_are_zero_based_per_source(self):
        """pair_index restarts at 0 for each source document and follows
        document order."""
        docs = [_doc(EN_PREFIX_FAQ), _doc(BOLD_FAQ)]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual([d.metadata["pair_index"] for d in result],
                         [0, 1, 0, 1])
        self.assertEqual([d.metadata["source_doc_id"] for d in result],
                         [docs[0].id, docs[0].id, docs[1].id, docs[1].id])

    def test_source_never_mutated_and_metadata_not_copied(self):
        """The source document object keeps text and metadata, pair
        documents do not inherit source metadata, and ids differ."""
        doc = _doc(EN_PREFIX_LONG_FAQ, lang="en", origin="manual.pdf")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.text, EN_PREFIX_LONG_FAQ)
        self.assertEqual(doc.metadata, {"lang": "en", "origin": "manual.pdf"})
        self.assertNotIn("lang", result[0].metadata)
        self.assertNotEqual(result[0].id, doc.id)

    def test_keep_source_false_replaces(self):
        """Default behavior: sources with pairs are replaced by their
        pair documents; sources without pairs stay."""
        docs = [_doc(EN_PREFIX_FAQ), _doc(NO_FAQ_PROSE)]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        self.assertEqual([d.metadata["source_doc_id"] for d in result[:2]],
                         [docs[0].id, docs[0].id])
        self.assertIs(result[2], docs[1])

    def test_keep_source_true_appends_after_source(self):
        """keep_source=True keeps every source in place and appends its
        pairs right after it."""
        docs = [_doc(EN_PREFIX_FAQ), _doc(NO_FAQ_PROSE)]
        self.extractor.keep_source = True
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(len(result), 4)
        self.assertIs(result[0], docs[0])
        self.assertEqual(result[1].metadata["source_doc_id"], docs[0].id)
        self.assertEqual(result[2].metadata["source_doc_id"], docs[0].id)
        self.assertIs(result[3], docs[1])

    # ========== Bounds tests ==========

    def test_min_answer_chars_filters_and_renumbers(self):
        """Answers below min_answer_chars are dropped and the surviving
        pairs are renumbered contiguously from 0."""
        text = ("Q: Short one?\n"
                "A: Yes.\n"
                "\n"
                "Q: Long one?\n"
                "A: This answer is deliberately long enough to pass.")
        self.extractor.min_answer_chars = 10
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(_pairs(result),
                         [("Long one?",
                           "This answer is deliberately long enough to pass.")])
        self.assertEqual(result[0].metadata["pair_index"], 0)

    def test_max_answer_chars_filters(self):
        """Answers above max_answer_chars are dropped, while 0 keeps the
        default unlimited behavior."""
        text = ("Q: Short one?\n"
                "A: Tiny.\n"
                "\n"
                "Q: Long one?\n"
                "A: This answer is deliberately long enough to be cut.")
        self.extractor.max_answer_chars = 20
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(_pairs(result), [("Short one?", "Tiny.")])
        self.extractor.max_answer_chars = 0
        result = self.extractor.process_docs([_doc(text)], self.query)
        self.assertEqual(len(result), 2)

    def test_max_pairs_caps_output(self):
        """At most max_pairs pairs are emitted, taking the first pairs
        in document order."""
        self.extractor.max_pairs = 2
        result = self.extractor.process_docs([_doc(MIXED_FAQ)], self.query)
        self.assertEqual(_pairs(result), MIXED_FAQ_PAIRS[:2])
        self.assertEqual([d.metadata["pair_index"] for d in result], [0, 1])

    def test_formats_selection(self):
        """Only the enabled detectors run: 'prefix' alone ignores
        heading blocks and 'heading' alone ignores prefix blocks."""
        doc = _doc(MIXED_FAQ)
        self.extractor.formats = ["prefix"]
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(_pairs(result), MIXED_FAQ_PAIRS[1:2])
        self.extractor.formats = ["heading"]
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(_pairs(result),
                         [MIXED_FAQ_PAIRS[0], MIXED_FAQ_PAIRS[3]])


if __name__ == '__main__':
    unittest.main()
