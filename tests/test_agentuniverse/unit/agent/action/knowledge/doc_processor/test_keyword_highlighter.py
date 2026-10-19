# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_keyword_highlighter.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.keyword_highlighter import KeywordHighlighter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A paragraph exercised by several tests: two 'alpha' occurrences of
# different case plus words that merely contain the letters.
ALPHA_TEXT = "The alpha release preceded the ALPHA sprint; alphanumeric codes stayed plain."

# 'new' occurs as a whole word once, but hides inside 'renewal' and
# 'newest' — the whole-word guard must reject both.
NEW_TEXT = "renewal newest new"

# CJK prose with no spaces: '模型' occurs twice, always glued to other
# characters, which is inherent to the script.
CJK_TEXT = "大模型时代与多模型架构"

# Overlap fixture: 'new' overlaps 'New York' only in the second sentence.
OVERLAP_TEXT = "a new deal in New York city"


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestKeywordHighlighter(unittest.TestCase):
    """Comprehensive test suite for KeywordHighlighter."""

    def setUp(self):
        self.highlighter = KeywordHighlighter()
        self.query = Query(query_str="highlighting")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _configured(self, config_dict) -> KeywordHighlighter:
        """Build a highlighter initialized through a component configer."""
        return KeywordHighlighter()._initialize_by_component_configer(
            self._create_configer(config_dict))

    # ========== Marker styles ==========

    def test_bold_style_ground_truth(self):
        """**kw** markers wrap every case-insensitive whole-word match."""
        h = self.highlighter
        h.keywords = ["alpha"]
        docs = h.process_docs([_doc(ALPHA_TEXT)], self.query)
        self.assertEqual(
            docs[0].text,
            "The **alpha** release preceded the **ALPHA** sprint; "
            "alphanumeric codes stayed plain.")
        self.assertEqual(docs[0].metadata["highlight_count"], 2)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["alpha"])

    def test_mark_style_ground_truth(self):
        """==kw== (Obsidian-style) markers wrap matches."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['risk'],
            'marker': 'mark',
        })
        text = "Risk assessment covers credit RISK and market risk."
        docs = h.process_docs([_doc(text)], self.query)
        self.assertEqual(
            docs[0].text,
            "==Risk== assessment covers credit ==RISK== and market ==risk==.")
        self.assertEqual(docs[0].metadata["highlight_count"], 3)

    def test_wiki_style_ground_truth(self):
        """[[kw]] (wiki link) markers wrap matches."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['agent'],
            'marker': 'wiki',
        })
        docs = h.process_docs(
            [_doc("The agent framework lets an Agent plan.")], self.query)
        self.assertEqual(docs[0].text,
                         "The [[agent]] framework lets an [[Agent]] plan.")

    def test_html_style_ground_truth(self):
        """<mark>kw</mark> markers wrap matches."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['data'],
            'marker': 'html',
        })
        docs = h.process_docs([_doc("Data quality matters.")], self.query)
        self.assertEqual(docs[0].text, "<mark>Data</mark> quality matters.")

    def test_custom_style_ground_truth(self):
        """marker='custom' uses marker_prefix / marker_suffix verbatim."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['kw'],
            'marker': 'custom',
            'marker_prefix': '<<',
            'marker_suffix': '>>',
        })
        docs = h.process_docs([_doc("kw here")], self.query)
        self.assertEqual(docs[0].text, "<<kw>> here")

    def test_custom_style_requires_both_markers(self):
        """'custom' without a non-empty prefix or suffix is rejected."""
        with self.assertRaises(ValueError):
            self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['kw'],
                'marker': 'custom',
                'marker_suffix': '>>',
            })
        with self.assertRaises(ValueError):
            self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['kw'],
                'marker': 'custom',
                'marker_prefix': '<<',
                'marker_suffix': '',
            })

    # ========== Case sensitivity ==========

    def test_case_insensitive_by_default(self):
        """Default matching folds case on both sides (see bold ground
        truth above); case_sensitive=True restricts to exact spelling."""
        h = self.highlighter
        h.keywords = ["Alpha"]
        h.case_sensitive = True
        docs = h.process_docs([_doc("alpha beta ALPHA")], self.query)
        self.assertEqual(docs[0].text, "alpha beta ALPHA")
        self.assertEqual(docs[0].metadata["highlight_count"], 0)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], [])

        h.case_sensitive = False
        docs = h.process_docs([_doc("alpha beta ALPHA")], self.query)
        self.assertEqual(docs[0].text, "**alpha** beta **ALPHA**")

    # ========== Whole-word guard ==========

    def test_whole_word_guard_blocks_embedded_matches(self):
        """'new' must not match inside 'renewal' or 'newest'."""
        h = self.highlighter
        h.keywords = ["new"]
        docs = h.process_docs([_doc(NEW_TEXT)], self.query)
        self.assertEqual(docs[0].text, "renewal newest **new**")
        self.assertEqual(docs[0].metadata["highlight_count"], 1)

    def test_whole_word_guard_disabled_matches_substrings(self):
        """whole_words=False drops the ASCII boundary fences."""
        h = self.highlighter
        h.keywords = ["new"]
        h.whole_words = False
        docs = h.process_docs([_doc("renewal")], self.query)
        self.assertEqual(docs[0].text, "re**new**al")
        self.assertEqual(docs[0].metadata["highlight_count"], 1)

    def test_underscore_counts_as_word_character(self):
        """'new' stays silent inside 'new_word' (underscore is a word
        character), but matches the standalone token."""
        h = self.highlighter
        h.keywords = ["new"]
        docs = h.process_docs([_doc("new_word and new")], self.query)
        self.assertEqual(docs[0].text, "new_word and **new**")

    # ========== CJK matching ==========

    def test_cjk_keyword_matches_without_spaces(self):
        """CJK keywords match while glued to surrounding characters —
        no spaces exist in the script, so occurrences are inherently
        whole-word."""
        h = self.highlighter
        h.keywords = ["模型"]
        docs = h.process_docs([_doc(CJK_TEXT)], self.query)
        self.assertEqual(docs[0].text, "大**模型**时代与多**模型**架构")
        self.assertEqual(docs[0].metadata["highlight_count"], 2)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["模型"])

    def test_ascii_boundary_is_ascii_only(self):
        """'AI' matches before a CJK character and before punctuation —
        the boundary fences only reject ASCII word characters."""
        h = self.highlighter
        h.keywords = ["AI"]
        docs = h.process_docs([_doc("AI模型与AI-powered")], self.query)
        self.assertEqual(docs[0].text, "**AI**模型与**AI**-powered")

    # ========== Overlap resolution ==========

    def test_longest_keyword_wins_on_overlap(self):
        """With 'new' and 'New York' configured, the phrase wins where
        they overlap and the term still matches standalone occurrences."""
        h = self.highlighter
        h.keywords = ["new", "New York"]
        docs = h.process_docs([_doc(OVERLAP_TEXT)], self.query)
        self.assertEqual(docs[0].text, "a **new** deal in **New York** city")
        self.assertEqual(docs[0].metadata["highlight_count"], 2)
        self.assertEqual(docs[0].metadata["highlighted_keywords"],
                         ["new", "New York"])

    def test_contained_keyword_not_double_marked(self):
        """'York' inside a 'New York' match is never separately marked."""
        h = self.highlighter
        h.keywords = ["York", "New York"]
        docs = h.process_docs([_doc("New York")], self.query)
        self.assertEqual(docs[0].text, "**New York**")
        self.assertEqual(docs[0].metadata["highlight_count"], 1)

    def test_longer_candidate_rejected_by_word_guard_falls_back(self):
        """When 'New York' fails its trailing boundary ('New Yorkshire'),
        the shorter 'York' is still evaluated — and also fenced out."""
        h = self.highlighter
        h.keywords = ["New York", "York"]
        docs = h.process_docs([_doc("New Yorkshire")], self.query)
        self.assertEqual(docs[0].text, "New Yorkshire")
        self.assertEqual(docs[0].metadata["highlight_count"], 0)

    # ========== Idempotence (second-pass no-op guard) ==========

    def test_second_pass_is_no_op(self):
        """Re-running the processor on its own output leaves text and
        stamped metadata byte-identical (markers are never doubled)."""
        h = self.highlighter
        h.keywords = ["alpha"]
        first = h.process_docs([_doc(ALPHA_TEXT)], self.query)[0]
        second = h.process_docs([first], self.query)[0]
        self.assertEqual(
            second.text,
            "The **alpha** release preceded the **ALPHA** sprint; "
            "alphanumeric codes stayed plain.")
        self.assertEqual(second.metadata["highlight_count"], 2)
        self.assertEqual(second.metadata["highlighted_keywords"], ["alpha"])

    def test_second_pass_no_op_for_every_style(self):
        """The skip guard works for all four presets plus custom."""
        styles = [
            ('bold', '**', '**'), ('mark', '==', '=='),
            ('wiki', '[[', ']]'), ('html', '<mark>', '</mark>'),
        ]
        for style, prefix, suffix in styles:
            h = self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['risk'],
                'marker': style,
            })
            once = h.process_docs([_doc("risk and RISK")], self.query)[0]
            expected = f"{prefix}risk{suffix} and {prefix}RISK{suffix}"
            self.assertEqual(once.text, expected, f"style={style}")
            twice = h.process_docs([once], self.query)[0]
            self.assertEqual(twice.text, expected, f"style={style}")
            self.assertEqual(twice.metadata["highlight_count"], 2,
                             f"style={style}")

    def test_second_pass_no_op_with_overlap_and_cap(self):
        """Guard-skipped matches count toward the cap, so a capped
        document stays untouched on a second pass."""
        h = self.highlighter
        h.keywords = ["new", "New York"]
        h.max_highlights = 2
        once = h.process_docs([_doc(OVERLAP_TEXT)], self.query)[0]
        # Cap 2 > the 2 matches here: both marked on the first pass.
        self.assertEqual(once.text, "a **new** deal in **New York** city")
        twice = h.process_docs([once], self.query)[0]
        self.assertEqual(twice.text, "a **new** deal in **New York** city")
        self.assertEqual(twice.metadata["highlight_count"], 2)

    # ========== Cap behavior ==========

    def test_cap_leaves_further_matches_unmarked_count_stays_total(self):
        """max_highlights bounds marked occurrences; highlight_count
        still reports every match found."""
        h = self.highlighter
        h.keywords = ["goal"]
        h.max_highlights = 3
        text = "goal one goal two goal three goal four goal five"
        docs = h.process_docs([_doc(text)], self.query)
        self.assertEqual(
            docs[0].text,
            "**goal** one **goal** two **goal** three goal four goal five")
        self.assertEqual(docs[0].metadata["highlight_count"], 5)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["goal"])

    def test_capped_document_second_pass_is_no_op(self):
        """Already-marked matches consume the cap, so the leftovers
        beyond it are not marked by a second pass either."""
        h = self.highlighter
        h.keywords = ["goal"]
        h.max_highlights = 3
        text = "goal one goal two goal three goal four goal five"
        once = h.process_docs([_doc(text)], self.query)[0]
        expected = ("**goal** one **goal** two **goal** three "
                    "goal four goal five")
        self.assertEqual(once.text, expected)
        twice = h.process_docs([once], self.query)[0]
        self.assertEqual(twice.text, expected)
        self.assertEqual(twice.metadata["highlight_count"], 5)

    def test_cap_of_one(self):
        """max_highlights=1 marks only the first occurrence."""
        h = self.highlighter
        h.keywords = ["solo"]
        h.max_highlights = 1
        docs = h.process_docs([_doc("solo solo solo")], self.query)
        self.assertEqual(docs[0].text, "**solo** solo solo")
        self.assertEqual(docs[0].metadata["highlight_count"], 3)

    # ========== Passthrough behavior ==========

    def test_no_keyword_match_passthrough_byte_identical(self):
        """Without a single match the text is returned byte-identical
        and zero counts are stamped."""
        h = self.highlighter
        h.keywords = ["zebra"]
        text = "alpha beta gamma\n\tsecond line\r\n"
        docs = h.process_docs([_doc(text)], self.query)
        self.assertEqual(docs[0].text, text)
        self.assertEqual(docs[0].metadata["highlight_count"], 0)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], [])

    def test_keywords_are_escaped_not_interpreted(self):
        """Regex metacharacters in keywords are literals: 'a.b' does not
        match 'axb' and 'C++' survives escaping."""
        h = self.highlighter
        h.keywords = ["a.b"]
        docs = h.process_docs([_doc("axb a.b")], self.query)
        self.assertEqual(docs[0].text, "axb **a.b**")

        h.keywords = ["C++"]
        docs = h.process_docs([_doc("C++ and C language")], self.query)
        self.assertEqual(docs[0].text, "**C++** and C language")

    # ========== Metadata stamping ==========

    def test_metadata_stamping_preserves_existing_entries(self):
        """highlight_count / highlighted_keywords are added alongside
        pre-existing metadata, on a copied mapping."""
        original = {"source": "news", "lang": "en"}
        h = self.highlighter
        h.keywords = ["alpha"]
        doc = Document(text="alpha here", metadata=dict(original))
        docs = h.process_docs([doc], self.query)
        self.assertEqual(docs[0].metadata["source"], "news")
        self.assertEqual(docs[0].metadata["lang"], "en")
        self.assertEqual(docs[0].metadata["highlight_count"], 1)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["alpha"])
        # The caller's mapping is not mutated in place.
        self.assertEqual(original, {"source": "news", "lang": "en"})

    def test_highlighted_keywords_lists_unique_configured_spellings(self):
        """highlighted_keywords carries configured spellings (not the
        matched casing), unique and in first-occurrence order."""
        h = self.highlighter
        h.keywords = ["gamma", "beta", "alpha"]
        docs = h.process_docs(
            [_doc("alpha here, ALPHA again, beta and GAMMA")], self.query)
        self.assertEqual(docs[0].metadata["highlight_count"], 4)
        self.assertEqual(docs[0].metadata["highlighted_keywords"],
                         ["alpha", "beta", "gamma"])

    def test_unmatched_keywords_are_not_listed(self):
        """Only keywords that actually matched appear in metadata."""
        h = self.highlighter
        h.keywords = ["alpha", "zebra"]
        docs = h.process_docs([_doc("alpha only")], self.query)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["alpha"])

    def test_documents_are_processed_independently(self):
        """Each document gets its own count and rewrite."""
        h = self.highlighter
        h.keywords = ["alpha"]
        docs = h.process_docs(
            [_doc("alpha one"), _doc("nothing here"), _doc("alpha alpha")],
            self.query)
        self.assertEqual(docs[0].text, "**alpha** one")
        self.assertEqual(docs[0].metadata["highlight_count"], 1)
        self.assertEqual(docs[1].text, "nothing here")
        self.assertEqual(docs[1].metadata["highlight_count"], 0)
        self.assertEqual(docs[2].text, "**alpha** **alpha**")
        self.assertEqual(docs[2].metadata["highlight_count"], 2)

    def test_empty_and_missing_text(self):
        """Empty text stays empty; None text stays None; both stamped."""
        h = self.highlighter
        h.keywords = ["alpha"]
        empty = Document(text="")
        # Assigned post-construction: Document's own validator rejects a
        # None text at creation time, but storage layers may still hand
        # such documents over.
        none_text = Document(text="")
        none_text.text = None
        docs = h.process_docs([empty, none_text], self.query)
        self.assertEqual(docs[0].text, "")
        self.assertIsNone(docs[1].text)
        for doc in docs:
            self.assertEqual(doc.metadata["highlight_count"], 0)
            self.assertEqual(doc.metadata["highlighted_keywords"], [])

    def test_empty_document_list(self):
        """An empty batch returns an empty list."""
        h = self.highlighter
        h.keywords = ["alpha"]
        self.assertEqual(h.process_docs([], self.query), [])

    def test_bare_instance_without_keywords_passthrough(self):
        """Directly constructed instance with no keywords passes text
        through unchanged instead of crashing."""
        docs = self.highlighter.process_docs([_doc("alpha")], self.query)
        self.assertEqual(docs[0].text, "alpha")
        self.assertEqual(docs[0].metadata["highlight_count"], 0)

    # ========== Determinism ==========

    def test_deterministic_output(self):
        """Two runs over equal inputs produce byte-identical results."""
        results = []
        for _ in range(2):
            h = KeywordHighlighter()
            h.keywords = ["new", "New York"]
            doc = h.process_docs([_doc(OVERLAP_TEXT)], self.query)[0]
            results.append((doc.text, tuple(sorted(doc.metadata.items()))))
        self.assertEqual(results[0], results[1])

    # ========== Configuration and validation ==========

    def test_default_configuration(self):
        """Defaults: bold style, insensitive, whole words, cap 200."""
        f = KeywordHighlighter()
        self.assertEqual(f.keywords, [])
        self.assertEqual(f.marker, "bold")
        self.assertFalse(f.case_sensitive)
        self.assertTrue(f.whole_words)
        self.assertEqual(f.max_highlights, 200)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['risk', 'exposure'],
            'marker': 'mark',
            'case_sensitive': True,
            'whole_words': False,
            'max_highlights': 5,
        })
        self.assertEqual(h.name, 'keyword_highlighter')
        self.assertEqual(h.description, 'keyword highlighter')
        self.assertEqual(h.keywords, ['risk', 'exposure'])
        self.assertEqual(h.marker, 'mark')
        self.assertTrue(h.case_sensitive)
        self.assertFalse(h.whole_words)
        self.assertEqual(h.max_highlights, 5)

    def test_keywords_are_stripped_and_duplicates_collapse(self):
        """Surrounding whitespace is stripped at load time; case-
        insensitive duplicates collapse to the first configured spelling
        when matching, so markers are never doubled."""
        h = self._configured({
            'name': 'keyword_highlighter',
            'description': 'keyword highlighter',
            'keywords': ['  agent ', 'Agent', 'agent'],
        })
        self.assertEqual(h.keywords, ['agent', 'Agent', 'agent'])
        docs = h.process_docs([_doc("agent and AGENT")], self.query)
        self.assertEqual(docs[0].text, "**agent** and **AGENT**")
        self.assertEqual(docs[0].metadata["highlight_count"], 2)
        self.assertEqual(docs[0].metadata["highlighted_keywords"], ["agent"])

    def test_invalid_marker_rejected(self):
        """Unknown marker style fails at load time."""
        with self.assertRaises(ValueError):
            self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['kw'],
                'marker': 'underline',
            })

    def test_invalid_max_highlights_rejected(self):
        """max_highlights must be an integer >= 1."""
        with self.assertRaises(ValueError):
            self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['kw'],
                'max_highlights': 0,
            })
        with self.assertRaises(ValueError):
            self._configured({
                'name': 'keyword_highlighter',
                'description': 'keyword highlighter',
                'keywords': ['kw'],
                'max_highlights': 'many',
            })

    def test_invalid_keywords_rejected(self):
        """keywords must be a list of non-empty strings."""
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter',
                              'description': 'kh',
                              'keywords': 'new'})
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter',
                              'description': 'kh',
                              'keywords': []})
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter', 'description': 'kh'})
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter',
                              'description': 'kh',
                              'keywords': ['ok', '']})
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter',
                              'description': 'kh',
                              'keywords': ['ok', '   ']})
        with self.assertRaises(ValueError):
            self._configured({'name': 'keyword_highlighter',
                              'description': 'kh',
                              'keywords': ['ok', 42]})

    def test_marker_styles_map_to_expected_pairs(self):
        """The four presets map to their documented marker pairs."""
        from agentuniverse.agent.action.knowledge.doc_processor.keyword_highlighter import MARKER_STYLES
        self.assertEqual(MARKER_STYLES['bold'], ('**', '**'))
        self.assertEqual(MARKER_STYLES['mark'], ('==', '=='))
        self.assertEqual(MARKER_STYLES['wiki'], ('[[', ']]'))
        self.assertEqual(MARKER_STYLES['html'], ('<mark>', '</mark>'))


if __name__ == "__main__":
    unittest.main()
