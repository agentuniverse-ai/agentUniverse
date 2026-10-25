# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_citation_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.citation_extractor import CitationExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Every text below is reused by the span-invariant sweep; ground truths
# are pinned per test.
TEXT_CURLY = 'She replied “we see steady demand” according to the central bank.'
TEXT_STRAIGHT = ('Jane opened with "The market is fundamentally strong," '
                 'said Jane Doe. and went on.')
TEXT_CJK = '“我们对市场充满信心，”张三表示。'
TEXT_ZH_SHUO = '“这个方法非常有效，”王教授说。'
TEXT_PRONOUN = '"It works," he said.'
TEXT_NO_ATTR = '"A plain quoted fragment" stands alone in the text.'
TEXT_LEAKY = '"Prices fell" yesterday. 张三表示 things were fine later.'
TEXT_NESTED_EN = '“She said ‘hi’ to everyone,” the aide explained.'
TEXT_NESTED_ZH = '「他说『你好』之后离开」的记录。'
TEXT_INNER_ALONE = '‘A quiet aside’ went unnoticed.'
TEXT_TWO_LINES = 'He said "alpha beta" once.\nShe wrote "gamma delta" twice.'
TEXT_ORPHAN = 'An orphan “ quote mark and an unused " one.'
TEXT_NUMERIC = ('Prior work [1] established the baseline; later studies '
                '[12] and [1,2] confirmed it, while [3-5] extended it.')
TEXT_AUTHOR_YEAR = ('This follows (Smith, 2026) and (Author et al., 2026a); '
                    'multi-author forms like (Wang & Li, 2026) and '
                    '(Smith, Jones and Lee, 2020) too.')
TEXT_KEYS = ('The result is reproducible [SMITH2026] and documented '
             '[Garcia2024a].')
TEXT_NON_CITATION = ('See [note] and [link] below; costs rose (in 2026) '
                     'and (2026) alike; the variable x^2y is unrelated.')
TEXT_DOI = ('The dataset is published at doi:10.1234/abc.def.2026 and '
            'mirrored at https://doi.org/10.1016/j.infsof.2023.11.005 '
            'for reference.')
TEXT_DOI_PERIOD = 'Broken links happen doi:10.9999/end.'
TEXT_ARXIV = ('The proof appeared in arXiv:2507.12345 and an early '
              'version at arXiv:2507.12345v2; the page is '
              'https://arxiv.org/abs/2507.09999.')
TEXT_FOOTNOTE = 'The claim is old¹²³ and disputed^12; see also^3.'
TEXT_MULTI = ('"Demand is robust," said the spokesman, while the report '
              '(Author, 2026) cites [4] and doi:10.5555/xyz; see also '
              'arXiv:2501.11111 and note¹.')
TEXT_PLAIN = 'Just plain prose without any markers at all.'

ALL_TEXTS = (
    TEXT_CURLY, TEXT_STRAIGHT, TEXT_CJK, TEXT_ZH_SHUO, TEXT_PRONOUN,
    TEXT_NO_ATTR, TEXT_LEAKY, TEXT_NESTED_EN, TEXT_NESTED_ZH,
    TEXT_INNER_ALONE, TEXT_TWO_LINES, TEXT_ORPHAN, TEXT_NUMERIC,
    TEXT_AUTHOR_YEAR, TEXT_KEYS, TEXT_NON_CITATION, TEXT_DOI,
    TEXT_DOI_PERIOD, TEXT_ARXIV, TEXT_FOOTNOTE, TEXT_MULTI, TEXT_PLAIN,
)

VALID_KINDS = {"quote", "bracket", "doi", "arxiv", "footnote"}
KIND_ORDER = ["quote", "bracket", "doi", "arxiv", "footnote"]


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestCitationExtractor(unittest.TestCase):
    """Comprehensive test suite for CitationExtractor."""

    def setUp(self):
        self.extractor = CitationExtractor()
        self.query = Query(query_str="citations")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _citations(self, text: str):
        """Run extraction on one document and return its citation list."""
        doc = _doc(text)
        self.extractor.process_docs([doc], self.query)
        return doc.metadata["citations"]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: cap 100, 'citations' / 'citation_count' keys."""
        e = CitationExtractor()
        self.assertEqual(e.max_citations, 100)
        self.assertEqual(e.citations_key, "citations")
        self.assertEqual(e.count_key, "citation_count")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'citation_extractor',
            'description': 'citation extractor',
            'max_citations': 5,
            'citations_key': 'cites',
            'count_key': 'n',
        })
        e = CitationExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.max_citations, 5)
        self.assertEqual(e.citations_key, "cites")
        self.assertEqual(e.count_key, "n")
        self.assertEqual(e.name, "citation_extractor")

    def test_invalid_configuration_raises(self):
        """Zero/negative/fractional/boolean caps and non-string keys all
        fail at load time."""
        base = {
            'name': 'e', 'description': 'd',
            'max_citations': 100,
            'citations_key': 'citations', 'count_key': 'citation_count',
        }
        for key, value in (
            ('max_citations', 0),
            ('max_citations', -3),
            ('max_citations', 2.5),
            ('max_citations', True),
            ('citations_key', 7),
            ('count_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                CitationExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Quote tests ==========

    def test_quote_curly_double_with_english_attribution(self):
        """Curly double quotation with an 'according to' attribution."""
        citations = self._citations(TEXT_CURLY)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["kind"], "quote")
        self.assertEqual(citations[0]["text"], "“we see steady demand”")
        self.assertEqual(citations[0]["attribution"],
                         "according to the central bank")

    def test_quote_straight_with_said_attribution(self):
        """Straight quotation (comma kept inside the marks) with a 'said'
        attribution; the later sentence is out of the window."""
        citations = self._citations(TEXT_STRAIGHT)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["text"],
                         '"The market is fundamentally strong,"')
        self.assertEqual(citations[0]["attribution"], "said Jane Doe")

    def test_quote_cjk_brackets_with_zh_attribution(self):
        """CJK corner-bracket quotation attributed by 表示; the ZH speaker
        precedes the verb right after the closing mark."""
        citations = self._citations(TEXT_CJK)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["kind"], "quote")
        self.assertEqual(citations[0]["text"], "“我们对市场充满信心，”")
        self.assertEqual(citations[0]["attribution"], "张三表示")

    def test_quote_cjk_with_shuo_attribution(self):
        """The single-character Chinese cue 说 is captured with its
        speaker as well."""
        citations = self._citations(TEXT_ZH_SHUO)
        self.assertEqual(citations[0]["attribution"], "王教授说")

    def test_quote_pronoun_attribution(self):
        """'he said' — the pronoun precedes the cue and is captured."""
        citations = self._citations(TEXT_PRONOUN)
        self.assertEqual(citations[0]["text"], '"It works,"')
        self.assertEqual(citations[0]["attribution"], "he said")

    def test_quote_without_attribution_is_null(self):
        """A quotation without any nearby cue keeps attribution None."""
        citations = self._citations(TEXT_NO_ATTR)
        self.assertEqual(len(citations), 1)
        self.assertIsNone(citations[0]["attribution"])

    def test_attribution_window_stops_at_sentence_end(self):
        """A cue in the NEXT sentence never leaks into the attribution."""
        citations = self._citations(TEXT_LEAKY)
        self.assertEqual(len(citations), 1)
        self.assertIsNone(citations[0]["attribution"])

    def test_nested_inner_quotes_not_double_counted(self):
        """Inner quote styles inside an outer quotation are not counted
        separately — English curly singles and CJK white corners."""
        for text, expected in (
            (TEXT_NESTED_EN, "“She said ‘hi’ to everyone,”"),
            (TEXT_NESTED_ZH, "「他说『你好』之后离开」"),
        ):
            citations = self._citations(text)
            self.assertEqual(len(citations), 1, text)
            self.assertEqual(citations[0]["kind"], "quote")
            self.assertEqual(citations[0]["text"], expected)

    def test_standalone_inner_style_quote_counted(self):
        """A curly-single quotation OUTSIDE any outer quotation is still
        reported as a quote."""
        citations = self._citations(TEXT_INNER_ALONE)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["text"], "‘A quiet aside’")
        self.assertIsNone(citations[0]["attribution"])

    def test_straight_quotes_pair_within_lines(self):
        """Straight marks pair left to right per line and never across
        the newline."""
        citations = self._citations(TEXT_TWO_LINES)
        self.assertEqual([c["text"] for c in citations],
                         ['"alpha beta"', '"gamma delta"'])

    def test_unmatched_quote_marks_ignored(self):
        """Orphan opening marks produce no citation."""
        self.assertEqual(self._citations(TEXT_ORPHAN), [])

    # ========== Bracket citation tests ==========

    def test_bracket_numeric_markers(self):
        """[1], [12], list and range forms all match as one marker each."""
        citations = self._citations(TEXT_NUMERIC)
        self.assertEqual([c["kind"] for c in citations],
                         ["bracket"] * 4)
        self.assertEqual([c["text"] for c in citations],
                         ["[1]", "[12]", "[1,2]", "[3-5]"])

    def test_bracket_author_year_forms(self):
        """(Author, YEAR), et al. with a suffix letter, ampersand and
        multi-author 'and' forms."""
        citations = self._citations(TEXT_AUTHOR_YEAR)
        self.assertEqual([c["text"] for c in citations],
                         ["(Smith, 2026)", "(Author et al., 2026a)",
                          "(Wang & Li, 2026)",
                          "(Smith, Jones and Lee, 2020)"])

    def test_bracket_alphanumeric_keys(self):
        """Citation keys like [SMITH2026] match."""
        citations = self._citations(TEXT_KEYS)
        self.assertEqual([c["text"] for c in citations],
                         ["[SMITH2026]", "[Garcia2024a]"])

    def test_non_citation_brackets_ignored(self):
        """Bracketed words without digits, bare years in parentheses and
        caret-glued variables produce nothing."""
        self.assertEqual(self._citations(TEXT_NON_CITATION), [])

    # ========== DOI / arXiv / footnote tests ==========

    def test_doi_markers(self):
        """Both doi: prefix and resolver URL forms match with the full
        suffix."""
        citations = self._citations(TEXT_DOI)
        self.assertEqual([c["kind"] for c in citations], ["doi"] * 2)
        self.assertEqual([c["text"] for c in citations],
                         ["doi:10.1234/abc.def.2026",
                          "https://doi.org/10.1016/j.infsof.2023.11.005"])

    def test_doi_trailing_period_trimmed(self):
        """A sentence-final period after a DOI is not part of the marker,
        and the span still reproduces the trimmed text."""
        citations = self._citations(TEXT_DOI_PERIOD)
        self.assertEqual(citations[0]["text"], "doi:10.9999/end")
        start, end = citations[0]["span"]
        self.assertEqual(TEXT_DOI_PERIOD[start:end], "doi:10.9999/end")

    def test_arxiv_markers(self):
        """arXiv: ids with and without a version tag, plus the abs URL."""
        citations = self._citations(TEXT_ARXIV)
        self.assertEqual([c["kind"] for c in citations], ["arxiv"] * 3)
        self.assertEqual([c["text"] for c in citations],
                         ["arXiv:2507.12345", "arXiv:2507.12345v2",
                          "https://arxiv.org/abs/2507.09999"])

    def test_footnote_markers(self):
        """Superscript digit runs and caret markers (but not caret-glued
        words) match."""
        citations = self._citations(TEXT_FOOTNOTE)
        self.assertEqual([c["kind"] for c in citations],
                         ["footnote"] * 3)
        self.assertEqual([c["text"] for c in citations],
                         ["¹²³", "^12", "^3"])

    # ========== Multi-citation / span / shape tests ==========

    def test_multi_citation_document(self):
        """All five kinds in one document: span order, attribution and the
        per-kind tally."""
        citations = self._citations(TEXT_MULTI)
        self.assertEqual([c["kind"] for c in citations],
                         ["quote", "bracket", "bracket", "doi", "arxiv",
                          "footnote"])
        self.assertEqual([c["text"] for c in citations],
                         ['"Demand is robust,"', "(Author, 2026)", "[4]",
                          "doi:10.5555/xyz", "arXiv:2501.11111", "¹"])
        self.assertEqual(citations[0]["attribution"],
                         "said the spokesman")
        self.assertTrue(all(c["attribution"] is None
                            for c in citations[1:]))

        doc = _doc(TEXT_MULTI)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["citation_count"],
                         {"quote": 1, "bracket": 2, "doi": 1, "arxiv": 1,
                          "footnote": 1})

    def test_span_invariant_on_all_texts(self):
        """Every citation's span reproduces its text exactly, kinds are
        valid, and spans are ordered and non-overlapping per kind pair
        where positions differ."""
        for text in ALL_TEXTS:
            for citation in self._citations(text):
                start, end = citation["span"]
                self.assertEqual(text[start:end], citation["text"],
                                 text[:40])
                self.assertIn(citation["kind"], VALID_KINDS)
        spans = [tuple(c["span"]) for c in self._citations(TEXT_MULTI)]
        self.assertEqual(spans, sorted(spans))

    def test_citation_entry_shape(self):
        """Entries carry exactly the four documented fields; spans are
        two-int lists; attribution is filled only for quotes."""
        for citation in self._citations(TEXT_MULTI):
            self.assertEqual(set(citation.keys()),
                             {"kind", "text", "attribution", "span"})
            self.assertIsInstance(citation["span"], list)
            self.assertEqual(len(citation["span"]), 2)
            self.assertTrue(all(isinstance(i, int)
                                for i in citation["span"]))
            if citation["kind"] != "quote":
                self.assertIsNone(citation["attribution"])

    def test_counts_key_order_fixed(self):
        """The count mapping always lists all five kinds in canonical
        order, zeros included."""
        doc = _doc(TEXT_PLAIN)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(list(doc.metadata["citation_count"].keys()),
                         KIND_ORDER)
        self.assertEqual(doc.metadata["citation_count"],
                         {"quote": 0, "bracket": 0, "doi": 0, "arxiv": 0,
                          "footnote": 0})

    # ========== Cap and passthrough tests ==========

    def test_cap_keeps_earliest_citations(self):
        """max_citations keeps the earliest markers only; the tally is
        computed over the kept list."""
        self.extractor.max_citations = 3
        doc = _doc('Refs [1] [2] [3] [4] [5] dot.')
        self.extractor.process_docs([doc], self.query)
        citations = doc.metadata["citations"]
        self.assertEqual([c["text"] for c in citations],
                         ["[1]", "[2]", "[3]"])
        self.assertEqual(doc.metadata["citation_count"]["bracket"], 3)
        self.assertEqual(
            sum(doc.metadata["citation_count"].values()),
            len(citations))

    def test_no_citation_passthrough(self):
        """A marker-free document passes through with empty lists, text
        and id untouched, and the same document object returned."""
        doc = _doc(TEXT_PLAIN, src="wire")
        result = self.extractor.process_docs([doc], self.query)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, TEXT_PLAIN)
        self.assertTrue(doc.id)
        self.assertEqual(doc.metadata["citations"], [])
        self.assertEqual(doc.metadata["src"], "wire")

    def test_metadata_copy_not_mutate(self):
        """Existing metadata survives; stamping writes through a copy so
        the caller's original mapping object gains no keys in place."""
        doc = _doc(TEXT_KEYS, source="wiki", rank=2)
        original_meta = doc.metadata
        self.extractor.process_docs([doc], self.query)

        self.assertEqual(doc.metadata["source"], "wiki")
        self.assertEqual(doc.metadata["rank"], 2)
        self.assertEqual(len(doc.metadata["citations"]), 2)
        self.assertNotIn("citations", original_meta)
        self.assertNotIn("citation_count", original_meta)
        self.assertIsNot(doc.metadata, original_meta)

    def test_metadata_none_document(self):
        """A document constructed without metadata receives a fresh
        mapping with the two stamps."""
        doc = Document(text=TEXT_KEYS)
        self.assertIsNone(doc.metadata)
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(set(doc.metadata.keys()),
                         {"citations", "citation_count"})
        self.assertEqual(len(doc.metadata["citations"]), 2)

    def test_disabled_keys_stamp_nothing(self):
        """Empty citations_key / count_key disable both stamps."""
        self.extractor.citations_key = ""
        self.extractor.count_key = ""
        doc = _doc(TEXT_KEYS, src="wire")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {"src": "wire"})

    def test_empty_batch_and_blank_text(self):
        """An empty batch yields an empty list; blank text yields no
        citations but is still stamped."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])

        doc = _doc("")
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["citations"], [])
        self.assertEqual(doc.metadata["citation_count"]["quote"], 0)

    def test_none_text_document(self):
        """A document whose text became None is tolerated."""
        doc = _doc("placeholder")
        doc.text = None
        self.extractor.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["citations"], [])

    def test_batch_documents_processed_independently(self):
        """Each document in a batch is annotated from its own text."""
        docs = [_doc(TEXT_KEYS), _doc(TEXT_PLAIN), _doc(TEXT_DOI)]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(docs[0].metadata["citations"]), 2)
        self.assertEqual(docs[1].metadata["citations"], [])
        self.assertEqual(len(docs[2].metadata["citations"]), 2)

    def test_deterministic_across_runs(self):
        """Repeated extraction of the same text yields identical lists."""
        first = self._citations(TEXT_MULTI)
        second = self._citations(TEXT_MULTI)
        third = self._citations(TEXT_MULTI)
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    # ========== Span ground truths ==========

    def test_span_positions_exact(self):
        """Hand-computed absolute offsets for one quotation and one
        marker."""
        citations = self._citations(TEXT_CURLY)
        start = TEXT_CURLY.index("“")
        end = TEXT_CURLY.index("”") + 1
        self.assertEqual(citations[0]["span"], [start, end])

        citations = self._citations(TEXT_NUMERIC)
        self.assertEqual(citations[0]["span"],
                         [TEXT_NUMERIC.index("[1]"),
                          TEXT_NUMERIC.index("[1]") + 3])


if __name__ == '__main__':
    unittest.main()
