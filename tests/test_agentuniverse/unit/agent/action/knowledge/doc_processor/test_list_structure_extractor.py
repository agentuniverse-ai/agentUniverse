# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_list_structure_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.list_structure_extractor import ListStructureExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Six consecutive items in six DIFFERENT bullet styles: every style
# change restarts the block, so this document yields six one-item
# blocks.
MIXED_BULLET_DOC = (
    "Shopping:\n"
    "- bread\n"
    "* milk\n"
    "• cheese\n"
    "· tea\n"
    "– coffee\n"
    "— sugar\n"
)

# Numbered items across families: '1.' and '1)' are distinct families,
# '(a)' and '(A)' share the letter-paren family (grouped together),
# '(一)' opens the cjk-paren family.
NUMBERED_DOC = (
    "1. alpha\n"
    "1) beta\n"
    "(a) gamma\n"
    "(A) delta\n"
    "(一) epsilon\n"
)

# Task checkboxes in three styles: dash-prefixed, asterisk-prefixed and
# bare boxes; x and X (but not space) count as checked.
CHECKBOX_DOC = (
    "- [ ] write tests\n"
    "- [x] run suite\n"
    "- [X] ship it\n"
    "* [ ] star repo\n"
    "[ ] bare item\n"
    "[x] bare done\n"
)

# One bullet list nested by two-space indents; the last line carries
# ten spaces (level 5) which must clamp to the maximum depth of 4.
NESTED_DOC = (
    "- top\n"
    "  - second\n"
    "    - third\n"
    "      - fourth\n"
    "        - fifth\n"
    "          - sixth\n"
)

# A prose line between two bullet runs: each side becomes its own
# block and the block spans skip the sentence.
PROSE_BREAK_DOC = (
    "- alpha\n"
    "- beta\n"
    "A plain sentence breaks the run.\n"
    "- gamma\n"
)


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestListStructureExtractor(unittest.TestCase):
    """Comprehensive test suite for ListStructureExtractor."""

    def setUp(self):
        self.extractor = ListStructureExtractor()
        self.query = Query(query_str="list structure")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _process_one(self, text: str):
        """Run the extractor over a single document and return it."""
        doc = _doc(text)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        return result[0]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 20 blocks / 100 items per block recorded."""
        e = ListStructureExtractor()
        self.assertEqual(e.max_lists, 20)
        self.assertEqual(e.max_items_per_list, 100)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'list_structure_extractor',
            'description': 'list structure extractor',
            'max_lists': 5,
            'max_items_per_list': 7,
        })
        e = ListStructureExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.max_lists, 5)
        self.assertEqual(e.max_items_per_list, 7)
        self.assertEqual(e.name, "list_structure_extractor")

    def test_invalid_configuration_raises(self):
        """Non-integer or < 1 caps fail at load time, including the
        bool trap (bool is an int subclass)."""
        base = {
            'name': 'e', 'description': 'd',
            'max_lists': 20, 'max_items_per_list': 100,
        }
        for key, value in (
            ('max_lists', 0),
            ('max_lists', -1),
            ('max_lists', 2.5),
            ('max_lists', True),
            ('max_lists', '5'),
            ('max_items_per_list', 0),
            ('max_items_per_list', -3),
            ('max_items_per_list', 1.5),
            ('max_items_per_list', False),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                ListStructureExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Bullet detection tests ==========

    def test_all_bullet_markers_detected(self):
        """-, *, •, ·, en dash and em dash all yield bullet items with
        their literal marker; each style change restarts the block."""
        doc = self._process_one(MIXED_BULLET_DOC)
        self.assertEqual(doc.metadata["list_count"], 6)
        lists = doc.metadata["lists"]
        self.assertEqual(len(lists), 6)
        self.assertEqual([block["kind"] for block in lists],
                         ["bullet"] * 6)
        self.assertEqual([block["items"][0]["marker"] for block in lists],
                         ["-", "*", "•", "·", "–", "—"])
        self.assertEqual([block["items"][0]["text"] for block in lists],
                         ["bread", "milk", "cheese", "tea",
                          "coffee", "sugar"])
        # No checkboxes anywhere: the summary key must be absent.
        self.assertNotIn("checkbox_summary", doc.metadata)

    def test_same_style_items_group_into_one_block(self):
        """Consecutive '-' items form a single multi-item block."""
        doc = self._process_one("- alpha\n- beta\n- gamma\n")
        self.assertEqual(doc.metadata["list_count"], 1)
        block = doc.metadata["lists"][0]
        self.assertEqual(block["kind"], "bullet")
        self.assertEqual(block["item_count"], 3)
        self.assertEqual([item["text"] for item in block["items"]],
                         ["alpha", "beta", "gamma"])
        self.assertEqual([item["marker"] for item in block["items"]],
                         ["-", "-", "-"])

    def test_numbered_families_and_grouping(self):
        """'1.' and '1)' open their own families; '(a)' and '(A)' share
        the letter-paren family; '(一)' opens the cjk-paren family."""
        doc = self._process_one(NUMBERED_DOC)
        self.assertEqual(doc.metadata["list_count"], 4)
        blocks = doc.metadata["lists"]
        self.assertEqual([b["kind"] for b in blocks],
                         ["numbered"] * 4)
        self.assertEqual([b["item_count"] for b in blocks],
                         [1, 1, 2, 1])
        self.assertEqual([item["marker"] for b in blocks
                          for item in b["items"]],
                         ["1.", "1)", "(a)", "(A)", "(一)"])
        self.assertEqual([item["text"] for b in blocks
                          for item in b["items"]],
                         ["alpha", "beta", "gamma", "delta",
                          "epsilon"])

    def test_numbered_sequence_same_family_one_block(self):
        """1. / 2. / 3. share the arabic-dot family regardless of the
        numbers actually used; sequence continuity is not enforced."""
        doc = self._process_one("1. one\n2. two\n7. seven\n")
        self.assertEqual(doc.metadata["list_count"], 1)
        self.assertEqual(doc.metadata["lists"][0]["item_count"], 3)

    # ========== Checkbox detection tests ==========

    def test_checkbox_items_and_checked_state(self):
        """Dash-, asterisk- and bare-box checkboxes are captured with
        their checked state; x/X mark checked, space unchecked."""
        doc = self._process_one(CHECKBOX_DOC)
        self.assertEqual(doc.metadata["list_count"], 3)
        items = [item for block in doc.metadata["lists"]
                 for item in block["items"]]
        self.assertEqual([item["marker"] for item in items],
                         ["- [ ]", "- [x]", "- [X]", "* [ ]",
                          "[ ]", "[x]"])
        self.assertEqual([item["checked"] for item in items],
                         [False, True, True, False, False, True])
        self.assertEqual([item["text"] for item in items],
                         ["write tests", "run suite", "ship it",
                          "star repo", "bare item", "bare done"])
        self.assertEqual(doc.metadata["checkbox_summary"],
                         {"total": 6, "checked": 3})

    def test_checkbox_summary_counts_mixed_documents(self):
        """Bullet and numbered items never leak into the checkbox
        summary; nested checkbox levels still count."""
        text = "- plain bullet\n1. numbered step\n- [ ] parent\n  - [x] child\n"
        doc = self._process_one(text)
        self.assertEqual(doc.metadata["list_count"], 3)
        self.assertEqual(doc.metadata["checkbox_summary"],
                         {"total": 2, "checked": 1})
        nested = doc.metadata["lists"][2]["items"]
        self.assertEqual([item["level"] for item in nested], [0, 1])
        self.assertEqual([item["checked"] for item in nested],
                         [False, True])

    def test_checked_key_only_on_checkbox_items(self):
        """'checked' appears on checkbox items only — never on bullet
        or numbered items."""
        text = "- bullet\n1. numbered\n- [ ] box\n"
        doc = self._process_one(text)
        all_items = [item for block in doc.metadata["lists"]
                     for item in block["items"]]
        kinds = [(block["kind"], item) for block in doc.metadata["lists"]
                 for item in block["items"]]
        for kind, item in kinds:
            if kind == "checkbox":
                self.assertIn("checked", item)
            else:
                self.assertNotIn("checked", item)

    # ========== Nesting tests ==========

    def test_nesting_levels_from_two_space_indents(self):
        """Two spaces per level; the sixth line's ten spaces (level 5)
        clamp to the maximum depth of 4."""
        doc = self._process_one(NESTED_DOC)
        self.assertEqual(doc.metadata["list_count"], 1)
        items = doc.metadata["lists"][0]["items"]
        self.assertEqual([item["level"] for item in items],
                         [0, 1, 2, 3, 4, 4])

    def test_nesting_levels_from_tabs(self):
        """One tab counts as one full nesting level."""
        doc = self._process_one("- a\n\t- b\n\t\t- c\n")
        items = doc.metadata["lists"][0]["items"]
        self.assertEqual([item["level"] for item in items], [0, 1, 2])

    def test_single_space_indent_keeps_top_level(self):
        """A single stray space does not create a nesting level."""
        doc = self._process_one("- top\n - still top\n")
        items = doc.metadata["lists"][0]["items"]
        self.assertEqual([item["level"] for item in items], [0, 0])

    # ========== Block boundary tests ==========

    def test_prose_line_breaks_block(self):
        """A non-list sentence between two bullet runs closes the open
        block; each side becomes its own block."""
        doc = self._process_one(PROSE_BREAK_DOC)
        self.assertEqual(doc.metadata["list_count"], 2)
        blocks = doc.metadata["lists"]
        self.assertEqual([b["item_count"] for b in blocks], [2, 1])
        self.assertEqual([b["span"] for b in blocks],
                         [[0, 14], [48, 55]])

    def test_blank_line_breaks_block(self):
        """Blank lines are non-list lines and close the open block."""
        doc = self._process_one("- a\n- b\n\n- c\n")
        self.assertEqual(doc.metadata["list_count"], 2)
        self.assertEqual(doc.metadata["lists"][0]["span"], [0, 7])

    def test_mixed_marker_change_restarts_block(self):
        """Switching bullet style mid-run splits blocks even without
        intervening prose; switching back splits again."""
        doc = self._process_one("- a\n* b\n- c\n")
        self.assertEqual(doc.metadata["list_count"], 3)
        self.assertEqual([b["items"][0]["marker"]
                          for b in doc.metadata["lists"]],
                         ["-", "*", "-"])

    def test_numbered_family_change_restarts_block(self):
        """'1.' followed by '1)' starts a second numbered block."""
        doc = self._process_one("1. a\n1) b\n")
        self.assertEqual(doc.metadata["list_count"], 2)
        self.assertEqual([b["item_count"]
                          for b in doc.metadata["lists"]], [1, 1])

    # ========== Non-list recognition tests ==========

    def test_numbered_looking_prose_not_matched(self):
        """Decimal numbers, multi-letter parentheses, unspaced markers,
        bold spans and horizontal rules are prose, not list items."""
        text = (
            "1.5 million units shipped\n"
            "(see annex) for details\n"
            "3)unspaced stays prose\n"
            "**bold** opening\n"
            "---\n"
            "--force is a flag\n"
        )
        doc = self._process_one(text)
        self.assertFalse(doc.metadata)
        self.assertNotIn("lists", doc.metadata or {})
        self.assertNotIn("list_count", doc.metadata or {})

    def test_indented_items_still_recognized(self):
        """Leading indentation applies to nesting, not recognition."""
        doc = self._process_one("  - indented\n    * deeper\n")
        self.assertEqual(doc.metadata["list_count"], 2)
        items = [item for b in doc.metadata["lists"]
                 for item in b["items"]]
        self.assertEqual([item["level"] for item in items], [1, 2])

    def test_empty_items_captured_with_empty_text(self):
        """A marker standing alone (or followed by spaces only) is an
        item whose text is the empty string."""
        doc = self._process_one("-\n- \n1.\n")
        self.assertEqual(doc.metadata["list_count"], 2)
        blocks = doc.metadata["lists"]
        self.assertEqual([item["text"] for item in blocks[0]["items"]],
                         ["", ""])
        self.assertEqual(blocks[1]["items"][0]["text"], "")

    # ========== Span invariant tests ==========

    def test_item_spans_cover_raw_lines(self):
        """Item spans reproduce the exact raw line — indentation and
        marker included — at the documented character offsets."""
        doc = self._process_one(PROSE_BREAK_DOC)
        items = [item for b in doc.metadata["lists"]
                 for item in b["items"]]
        self.assertEqual([doc.text[s:e] for s, e in
                          (item["span"] for item in items)],
                         ["- alpha", "- beta", "- gamma"])

    def test_span_invariants_hold(self):
        """Block spans start/end on their first/last item; item spans
        are ordered, non-overlapping and inside the text; the block
        region is exactly the item lines joined by newlines."""
        for text in (MIXED_BULLET_DOC, NUMBERED_DOC, CHECKBOX_DOC,
                     NESTED_DOC, PROSE_BREAK_DOC):
            doc = self._process_one(text)
            previous_end = 0
            for block in doc.metadata["lists"]:
                items = block["items"]
                start, end = block["span"]
                self.assertEqual(start, items[0]["span"][0])
                self.assertEqual(end, items[-1]["span"][1])
                self.assertLessEqual(start, end)
                for item in items:
                    s, e = item["span"]
                    self.assertGreaterEqual(s, previous_end)
                    self.assertGreaterEqual(s, 0)
                    self.assertLessEqual(e, len(text))
                    self.assertLessEqual(s, e)
                    previous_end = e
                self.assertEqual(
                    text[start:end],
                    "\n".join(text[s:e] for s, e in
                              (item["span"] for item in items)))

    def test_crlf_input_detected_with_clean_spans(self):
        """CRLF line endings are parsed; the carriage return is kept
        out of item spans."""
        text = "- a\r\n- b\r\n"
        doc = self._process_one(text)
        self.assertEqual(doc.metadata["list_count"], 1)
        items = doc.metadata["lists"][0]["items"]
        self.assertEqual([item["span"] for item in items],
                         [[0, 3], [5, 8]])
        self.assertEqual(text[0:3], "- a")

    # ========== Caps and totals tests ==========

    def test_max_lists_cap_keeps_true_count(self):
        """Only the first max_lists blocks are recorded while
        list_count reports every detected block."""
        text = "- a\n- b\n- c\nprose\n- d\n- e\n"
        self.extractor.max_lists = 1
        doc = self._process_one(text)
        self.assertEqual(doc.metadata["list_count"], 2)
        self.assertEqual(len(doc.metadata["lists"]), 1)
        self.assertEqual(doc.metadata["lists"][0]["span"], [0, 11])

    def test_max_items_per_list_cap_keeps_true_count(self):
        """The items payload is trimmed to max_items_per_list while
        item_count keeps the true total."""
        self.extractor.max_items_per_list = 2
        doc = self._process_one("- a\n- b\n- c\n- d\n- e\n")
        block = doc.metadata["lists"][0]
        self.assertEqual(block["item_count"], 5)
        self.assertEqual([item["text"] for item in block["items"]],
                         ["a", "b"])

    def test_checkbox_summary_counts_beyond_caps(self):
        """Checkbox totals stay accurate even when the blocks carrying
        them were trimmed out of the recorded payload."""
        text = "- [ ] a\n- [x] b\nprose\n- [ ] c\n"
        self.extractor.max_lists = 1
        doc = self._process_one(text)
        self.assertEqual(len(doc.metadata["lists"]), 1)
        self.assertEqual(doc.metadata["list_count"], 2)
        self.assertEqual(doc.metadata["checkbox_summary"],
                         {"total": 3, "checked": 1})

    # ========== Passthrough and metadata tests ==========

    def test_no_lists_passthrough(self):
        """Documents without any list are returned untouched: no lists
        keys stamped, metadata object unchanged."""
        text = "Just prose here.\nNo lists at all.\n"
        doc = _doc(text)
        result = self.extractor.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        self.assertIsNone(doc.metadata)

    def test_blank_text_documents(self):
        """Empty and whitespace-only texts pass through unstamped; an
        empty batch yields an empty result."""
        self.assertEqual(self.extractor.process_docs([], self.query),
                         [])
        for text in ("", "\n\n\n", "   \n\t\n"):
            doc = _doc(text)
            result = self.extractor.process_docs([doc], self.query)
            self.assertEqual(len(result), 1)
            self.assertIsNone(result[0].metadata)

    def test_existing_metadata_preserved_and_not_mutated(self):
        """Pre-existing metadata survives stamping; the new keys are
        written through a copy, never in place."""
        doc = _doc("- a\n", source="spec", rank=1)
        original_meta = doc.metadata
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["source"], "spec")
        self.assertEqual(result[0].metadata["rank"], 1)
        self.assertIn("lists", result[0].metadata)
        self.assertNotIn("lists", original_meta)
        self.assertIsNot(doc.metadata, original_meta)

    def test_batch_documents_processed_independently(self):
        """Each document is stamped from its own text; order and
        membership are preserved."""
        docs = [
            _doc("- bullet only\n"),
            _doc("prose only, nothing to detect\n"),
            _doc("- [x] done\n- [ ] pending\n"),
        ]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        self.assertIs(result[0], docs[0])
        self.assertIs(result[1], docs[1])
        self.assertIs(result[2], docs[2])
        self.assertEqual(result[0].metadata["list_count"], 1)
        self.assertNotIn("lists", result[1].metadata or {})
        self.assertEqual(result[2].metadata["checkbox_summary"],
                         {"total": 2, "checked": 1})

    # ========== Determinism tests ==========

    def test_deterministic_output(self):
        """Two fresh instances produce byte-identical metadata for the
        same input, and repeated runs are stable."""
        first = self._process_one(MIXED_BULLET_DOC + CHECKBOX_DOC)
        second_extractor = ListStructureExtractor()
        second_doc = _doc(MIXED_BULLET_DOC + CHECKBOX_DOC)
        second_extractor.process_docs([second_doc], self.query)
        self.assertEqual(first.metadata["lists"],
                         second_doc.metadata["lists"])
        self.assertEqual(first.metadata["list_count"],
                         second_doc.metadata["list_count"])
        self.assertEqual(first.metadata["checkbox_summary"],
                         second_doc.metadata["checkbox_summary"])
        again = self.extractor.process_docs(
            [_doc(MIXED_BULLET_DOC + CHECKBOX_DOC)], self.query)
        self.assertEqual(again[0].metadata, first.metadata)

    def test_text_and_id_untouched(self):
        """Document text and id are never modified by stamping."""
        doc = _doc(NESTED_DOC)
        doc_id = doc.id
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.text, NESTED_DOC)
        self.assertEqual(doc.id, doc_id)


if __name__ == '__main__':
    unittest.main()
