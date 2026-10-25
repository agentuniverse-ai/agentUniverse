# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_regex_filter.py

import re
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.regex_filter import RegexFilter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Ground-truth sample documents. Every assertion below is pinned against
# these exact strings, so a regex engine change would be caught.

ERR_TEXT = "Request failed with error ERR-4021 after 3 retries"

INVOICE_TEXT = "INVOICE-2026-041 total amount due within 30 days"

# Matches BOTH the error-code and the invoice pattern — the require_all probe.
MIXED_TEXT = "Processing failed: ERR-4021 referenced by INVOICE-2026-041"

DISCLAIMER_TEXT = ("This document is provided for informational purposes "
                   "only and does not constitute legal advice")

CHINESE_TEXT = "合同编号：HT-2026-042，本条款适用于双方签署的所有子合同。"

LOG_TEXT = "2026-10-19 04:12:07 WARN disk usage at 91% on /dev/sda1"

P_ERR = r"ERR-\d+"
P_INVOICE = r"INVOICE-\d{4}-\d{3}"
P_CN = r"合同编号："


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestRegexFilter(unittest.TestCase):
    """Comprehensive test suite for RegexFilter."""

    def setUp(self):
        self.filter = RegexFilter()
        self.query = Query(query_str="regex filtering")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _configured(self, **kwargs) -> RegexFilter:
        """Build a filter initialized through a component configer."""
        f = RegexFilter()
        config = {'name': 'regex_filter', 'description': 'regex filter'}
        config.update(kwargs)
        f._initialize_by_component_configer(self._create_configer(config))
        return f

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: no patterns, keep_matching, any-match, case sensitive,
        'regex_matched' metadata key."""
        f = RegexFilter()
        self.assertEqual(f.patterns, [])
        self.assertEqual(f.mode, "keep_matching")
        self.assertFalse(f.require_all)
        self.assertTrue(f.case_sensitive)
        self.assertEqual(f.matched_key, "regex_matched")

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization; a tuple
        pattern list is accepted and normalized to a list."""
        f = self._configured(patterns=[P_ERR, P_INVOICE],
                             mode='drop_matching',
                             require_all=True,
                             case_sensitive=False,
                             matched_key='hits')
        self.assertEqual(f.patterns, [P_ERR, P_INVOICE])
        self.assertEqual(f.mode, "drop_matching")
        self.assertTrue(f.require_all)
        self.assertFalse(f.case_sensitive)
        self.assertEqual(f.matched_key, "hits")
        self.assertEqual(f.name, "regex_filter")

        f_tuple = self._configured(patterns=(P_ERR,))
        self.assertEqual(f_tuple.patterns, [P_ERR])

    def test_invalid_configuration_raises(self):
        """Non-list patterns, non-string / empty-string / uncompilable
        entries, bad mode and non-string matched_key all fail at load
        time."""
        base = {
            'name': 'f', 'description': 'd',
            'patterns': [P_ERR], 'mode': 'keep_matching',
            'require_all': False, 'case_sensitive': True,
            'matched_key': 'regex_matched',
        }
        for key, value in (
            ('patterns', 'ERR-\\d+'),
            ('patterns', 42),
            ('patterns', [P_ERR, 7]),
            ('patterns', [P_ERR, '']),
            ('patterns', ['([unclosed']),
            ('patterns', ['*leading-quantifier']),
            ('mode', 'random'),
            ('mode', 'KEEP_MATCHING'),
            ('matched_key', 5),
            ('matched_key', ['x']),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                RegexFilter()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Matching semantics tests ==========

    def test_keep_matching_basic(self):
        """Default mode keeps documents where the pattern is found anywhere
        in the text (re.search, not re.match), preserving input order."""
        f = self._configured(patterns=[P_ERR])
        docs = [_doc(DISCLAIMER_TEXT), _doc(ERR_TEXT), _doc(INVOICE_TEXT),
                _doc("a second failure ERR-77 aborts the batch")]
        result = f.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], docs[1])
        self.assertIs(result[1], docs[3])

    def test_drop_matching(self):
        """drop_matching removes matching documents and keeps the rest."""
        f = self._configured(patterns=[P_ERR], mode='drop_matching')
        docs = [_doc(ERR_TEXT), _doc(DISCLAIMER_TEXT), _doc(INVOICE_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [DISCLAIMER_TEXT, INVOICE_TEXT])

    def test_multiple_patterns_any(self):
        """Several patterns combine with OR: a document matching any one of
        them survives."""
        f = self._configured(patterns=[P_ERR, P_INVOICE])
        docs = [_doc(ERR_TEXT), _doc(INVOICE_TEXT), _doc(CHINESE_TEXT),
                _doc(DISCLAIMER_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [ERR_TEXT, INVOICE_TEXT])

    def test_require_all_needs_every_pattern(self):
        """require_all switches to AND: only the document matching every
        pattern survives; single-pattern matches do not."""
        f = self._configured(patterns=[P_ERR, P_INVOICE], require_all=True)
        docs = [_doc(ERR_TEXT), _doc(INVOICE_TEXT), _doc(MIXED_TEXT),
                _doc(DISCLAIMER_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [MIXED_TEXT])

    def test_require_all_with_drop_matching(self):
        """Under require_all + drop_matching a partial match does not count:
        the mixed document alone is dropped, partial matches are kept."""
        f = self._configured(patterns=[P_ERR, P_INVOICE],
                             require_all=True, mode='drop_matching')
        docs = [_doc(ERR_TEXT), _doc(MIXED_TEXT), _doc(DISCLAIMER_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [ERR_TEXT, DISCLAIMER_TEXT])

    def test_anchor_and_character_class_syntax(self):
        """Standard regex syntax works: ^ anchors at text start, character
        classes and word boundaries behave exactly as in re.search."""
        f = self._configured(patterns=[r"^\d{4}-\d{2}-\d{2}"])
        docs = [_doc(LOG_TEXT), _doc("backup log mentions 2026-10-19 date")]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [LOG_TEXT])

        g = self._configured(patterns=[r"\bWARN\b"])
        self.assertEqual(
            [d.text for d in g.process_docs([_doc(LOG_TEXT),
                                             _doc("warning is lowercase")],
                                            self.query)],
            [LOG_TEXT])

    def test_unicode_pattern(self):
        """A CJK pattern matches the Chinese document and none of the
        English ones."""
        f = self._configured(patterns=[P_CN])
        docs = [_doc(CHINESE_TEXT), _doc(ERR_TEXT), _doc(DISCLAIMER_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [CHINESE_TEXT])

    def test_case_sensitive_default_and_ignorecase(self):
        """Default keeps standard re semantics ('err' does not hit
        'ERR-4021', '[A-Z]+' does not hit a lowercase-only text);
        case_sensitive=False compiles with re.IGNORECASE — where, as in re
        itself, [A-Z] also matches lowercase letters."""
        docs = [_doc(ERR_TEXT), _doc(DISCLAIMER_TEXT),
                _doc("disclaimer text with no capitals at all")]

        f = self._configured(patterns=[r"err-\d+"])
        self.assertEqual(f.process_docs(docs, self.query), [])

        f_ci = self._configured(patterns=[r"err-\d+"], case_sensitive=False)
        self.assertEqual([d.text for d in
                          f_ci.process_docs(docs, self.query)], [ERR_TEXT])

        upper_cs = self._configured(patterns=[r"[A-Z]+"])
        self.assertEqual([d.text for d in
                          upper_cs.process_docs(docs, self.query)],
                         [ERR_TEXT, DISCLAIMER_TEXT])

        upper_ci = self._configured(patterns=[r"[A-Z]+"],
                                    case_sensitive=False)
        self.assertEqual([d.text for d in
                          upper_ci.process_docs(docs, self.query)],
                         [ERR_TEXT, DISCLAIMER_TEXT,
                          "disclaimer text with no capitals at all"])

    def test_empty_patterns_is_noop(self):
        """An empty pattern list applies no constraint in either mode and
        stamps nothing."""
        docs = [_doc(ERR_TEXT), _doc(DISCLAIMER_TEXT)]
        for mode in ('keep_matching', 'drop_matching'):
            f = self._configured(patterns=[], mode=mode)
            result = f.process_docs(docs, self.query)
            self.assertEqual(result, docs)
            for doc in result:
                self.assertNotIn("regex_matched", doc.metadata or {})

    def test_empty_and_none_text(self):
        """None text is treated as the empty string; empty text still
        matches ^$ but not content patterns. (A None text cannot be built
        through the constructor — the Document id validator hashes the
        text — so it is assigned afterwards, as a pipeline may produce.)"""
        none_doc = _doc("placeholder")
        none_doc.text = None

        f_empty = self._configured(patterns=[r"^$"])
        docs = [_doc(""), none_doc, _doc(ERR_TEXT)]
        result = f_empty.process_docs(docs, self.query)
        self.assertEqual(len(result), 2)
        self.assertIsNone(result[1].text)

        f_content = self._configured(patterns=[P_ERR])
        blank = _doc("")
        blank.text = None
        self.assertEqual(
            f_content.process_docs([_doc(""), blank], self.query), [])

    def test_query_argument_ignored(self):
        """Matching depends only on document text: the query never changes
        the outcome."""
        f = self._configured(patterns=[P_ERR])
        docs = [_doc(ERR_TEXT), _doc(DISCLAIMER_TEXT)]
        self.assertEqual(f.process_docs(docs, self.query), [docs[0]])
        self.assertEqual(f.process_docs(docs, None), [docs[0]])
        self.assertEqual(f.process_docs(docs,
                                        Query(query_str="ERR-4021")),
                         [docs[0]])

    def test_invalid_direct_pattern_raises_re_error(self):
        """Patterns assigned directly as attributes bypass configer
        validation and surface as re.error at processing time."""
        f = RegexFilter()
        f.patterns = ["([unclosed"]
        with self.assertRaises(re.error):
            f.process_docs([_doc(ERR_TEXT)], self.query)

    # ========== Metadata bookkeeping tests ==========

    def test_metadata_matched_list_stamped(self):
        """Every processed document — kept and removed alike — carries the
        matched-pattern list in configuration order."""
        f = self._configured(patterns=[P_INVOICE, P_ERR])
        err, mixed, other = _doc(ERR_TEXT), _doc(MIXED_TEXT), \
            _doc(DISCLAIMER_TEXT)
        result = f.process_docs([err, mixed, other], self.query)

        self.assertEqual([d.text for d in result], [ERR_TEXT, MIXED_TEXT])
        self.assertEqual(err.metadata["regex_matched"], [P_ERR])
        self.assertEqual(mixed.metadata["regex_matched"],
                         [P_INVOICE, P_ERR])
        # Removed document is stamped too, so the drop reason is visible.
        self.assertEqual(other.metadata["regex_matched"], [])

    def test_metadata_stamped_in_drop_mode(self):
        """In drop mode the non-matching survivors carry an empty matched
        list and the dropped documents carry the patterns they hit."""
        f = self._configured(patterns=[P_ERR], mode='drop_matching')
        err, other = _doc(ERR_TEXT), _doc(DISCLAIMER_TEXT)
        result = f.process_docs([err, other], self.query)

        self.assertEqual(result, [other])
        self.assertEqual(other.metadata["regex_matched"], [])
        self.assertEqual(err.metadata["regex_matched"], [P_ERR])

    def test_metadata_copy_semantics(self):
        """Stamping writes through a copied mapping: the caller's original
        dict never gains keys in place, and pre-existing metadata entries
        survive on kept and removed documents alike."""
        err = _doc(ERR_TEXT, source="wire", rank=1)
        other = _doc(DISCLAIMER_TEXT, source="wire", rank=2)
        err_meta_ref, other_meta_ref = err.metadata, other.metadata

        f = self._configured(patterns=[P_ERR])
        result = f.process_docs([err, other], self.query)

        self.assertEqual(result, [err])
        self.assertEqual(err.metadata["source"], "wire")
        self.assertEqual(err.metadata["rank"], 1)
        self.assertEqual(err.metadata["regex_matched"], [P_ERR])
        self.assertEqual(other.metadata["rank"], 2)
        self.assertEqual(other.metadata["regex_matched"], [])
        self.assertNotIn("regex_matched", err_meta_ref)
        self.assertNotIn("regex_matched", other_meta_ref)
        self.assertIsNot(err.metadata, err_meta_ref)
        self.assertIsNot(other.metadata, other_meta_ref)

    def test_disabled_matched_key_stamps_nothing(self):
        """An empty matched_key disables stamping entirely."""
        f = self._configured(patterns=[P_ERR], matched_key='')
        err, other = _doc(ERR_TEXT, source="wire"), \
            _doc(DISCLAIMER_TEXT, source="wire")
        result = f.process_docs([err, other], self.query)

        self.assertEqual(result, [err])
        self.assertEqual(err.metadata, {"source": "wire"})
        self.assertEqual(other.metadata, {"source": "wire"})

    def test_duplicate_patterns_stamped_as_configured(self):
        """The pattern list is used verbatim: duplicates appear in the
        matched list exactly as configured."""
        f = self._configured(patterns=[P_ERR, P_ERR])
        err = _doc(ERR_TEXT)
        f.process_docs([err], self.query)
        self.assertEqual(err.metadata["regex_matched"], [P_ERR, P_ERR])

    # ========== Pipeline-shape tests ==========

    def test_empty_input(self):
        """Empty input yields empty output without touching anything."""
        f = self._configured(patterns=[P_ERR])
        self.assertEqual(f.process_docs([], self.query), [])

    def test_order_preserved(self):
        """Survivors keep the input's relative order across many docs."""
        f = self._configured(patterns=[P_ERR, P_CN])
        docs = [_doc(CHINESE_TEXT), _doc(DISCLAIMER_TEXT), _doc(ERR_TEXT),
                _doc(LOG_TEXT), _doc(MIXED_TEXT), _doc(INVOICE_TEXT)]
        result = f.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [CHINESE_TEXT, ERR_TEXT, MIXED_TEXT])

    def test_input_documents_not_corrupted(self):
        """Text and id are never modified by the filter."""
        err = _doc(ERR_TEXT)
        original_id = err.id
        f = self._configured(patterns=[P_ERR])
        result = f.process_docs([err], self.query)
        self.assertEqual(result[0].text, ERR_TEXT)
        self.assertEqual(result[0].id, original_id)

    def test_configer_round_trip_via_defaults(self):
        """A configer providing only name/description leaves every
        functional parameter at its default."""
        f = self._configured()
        self.assertEqual(f.patterns, [])
        self.assertEqual(f.mode, "keep_matching")
        docs = [_doc(ERR_TEXT)]
        self.assertEqual(f.process_docs(docs, self.query), docs)
        self.assertNotIn("regex_matched", docs[0].metadata or {})


if __name__ == '__main__':
    unittest.main()
