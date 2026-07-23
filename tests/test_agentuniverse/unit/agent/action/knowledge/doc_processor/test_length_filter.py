#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: test_length_filter.py

"""
Unit tests for the LengthFilter document processor.

These tests cover length measurement (char/word/token), the three drop
modes, bounds handling, order preservation, configer initialization and
validation.
"""

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.length_filter import (
    LengthFilter,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


class TestLengthFilter(unittest.TestCase):
    """Test suite for the LengthFilter component."""

    def setUp(self) -> None:
        self.filter = LengthFilter()
        # Documents with known character lengths: 5, 10, 20.
        self.docs = [
            Document(text='short'),                 # 5 chars
            Document(text='medium-len'),            # 10 chars
            Document(text='this-is-twenty-chars'),  # 20 chars
        ]

    # ---- length measurement ----

    def test_count_char(self) -> None:
        """counter='char' must return the exact character count."""
        f = LengthFilter(counter='char')
        self.assertEqual(f._count('hello'), 5)
        self.assertEqual(f._count(''), 0)

    def test_count_word(self) -> None:
        """counter='word' must return the whitespace word count."""
        f = LengthFilter(counter='word')
        self.assertEqual(f._count('hello world'), 2)
        self.assertEqual(f._count('one'), 1)
        self.assertEqual(f._count(''), 0)

    def test_count_token(self) -> None:
        """counter='token' must return a positive integer for non-empty text."""
        f = LengthFilter(counter='token')
        n = f._count('hello world')
        self.assertIsInstance(n, int)
        self.assertGreater(n, 0)

    # ---- drop modes ----

    def test_drop_short(self) -> None:
        """drop_short removes documents below min_length."""
        f = LengthFilter(min_length=10, counter='char', drop_mode='drop_short')
        result = f._process_docs(self.docs, None)
        # 'short' (5) is dropped; the rest (10, 20) are kept.
        self.assertEqual([d.text for d in result], ['medium-len', 'this-is-twenty-chars'])

    def test_drop_long(self) -> None:
        """drop_long removes documents above max_length."""
        f = LengthFilter(max_length=10, counter='char', drop_mode='drop_long')
        result = f._process_docs(self.docs, None)
        # 'this-is-twenty-chars' (20) is dropped; the rest (5, 10) are kept.
        self.assertEqual([d.text for d in result], ['short', 'medium-len'])

    def test_drop_both(self) -> None:
        """both removes documents outside [min_length, max_length]."""
        f = LengthFilter(min_length=6, max_length=15, counter='char',
                         drop_mode='both')
        result = f._process_docs(self.docs, None)
        # Only 'medium-len' (10) is within [6, 15].
        self.assertEqual([d.text for d in result], ['medium-len'])

    def test_drop_both_inclusive_bounds(self) -> None:
        """Bounds must be inclusive (== min/max length is kept)."""
        f = LengthFilter(min_length=10, max_length=10, counter='char',
                         drop_mode='both')
        result = f._process_docs(self.docs, None)
        self.assertEqual([d.text for d in result], ['medium-len'])

    # ---- order preservation & edge cases ----

    def test_preserves_order(self) -> None:
        """The relative order of the kept documents must be unchanged."""
        docs = [
            Document(text='x' * 100),
            Document(text='y' * 5),
            Document(text='z' * 100),
        ]
        f = LengthFilter(min_length=10, counter='char', drop_mode='drop_short')
        result = f._process_docs(docs, None)
        self.assertEqual([d.text for d in result], ['x' * 100, 'z' * 100])

    def test_empty_input(self) -> None:
        """An empty document list must return an empty list."""
        f = LengthFilter(min_length=10, counter='char')
        self.assertEqual(f._process_docs([], None), [])

    def test_no_filtering_when_bounds_disabled(self) -> None:
        """With min_length=0 and max_length=0 all documents are kept."""
        f = LengthFilter(min_length=0, max_length=0, counter='char',
                         drop_mode='both')
        result = f._process_docs(self.docs, None)
        self.assertEqual(len(result), 3)

    def test_empty_text_treated_as_zero(self) -> None:
        """Documents whose text is empty must be treated as length 0."""
        docs = [Document(text=''), Document(text='keepme')]
        f = LengthFilter(min_length=5, counter='char', drop_mode='drop_short')
        result = f._process_docs(docs, None)
        self.assertEqual([d.text for d in result], ['keepme'])

    def test_process_docs_public_interface(self) -> None:
        """The public process_docs wrapper must behave like _process_docs."""
        f = LengthFilter(min_length=10, counter='char')
        result = f.process_docs(self.docs, Query(query_str='ignored'))
        self.assertEqual([d.text for d in result], ['medium-len', 'this-is-twenty-chars'])

    # ---- configer initialization & validation ----

    def _make_configer(self, extra: dict) -> ComponentConfiger:
        cfg = Configer()
        value = {
            'name': 'length_filter',
            'description': 'filter by length',
        }
        value.update(extra)
        cfg.value = value
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def test_initialize_by_component_configer(self) -> None:
        """The configer must populate min/max length, counter and drop_mode."""
        configer = self._make_configer({
            'min_length': 8,
            'max_length': 100,
            'counter': 'word',
            'drop_mode': 'both',
        })
        f = LengthFilter()
        f._initialize_by_component_configer(configer)
        self.assertEqual(f.min_length, 8)
        self.assertEqual(f.max_length, 100)
        self.assertEqual(f.counter, 'word')
        self.assertEqual(f.drop_mode, 'both')

    def test_initialize_rejects_invalid_counter(self) -> None:
        """An unknown counter value must raise ValueError on init."""
        configer = self._make_configer({'counter': 'bytes'})
        f = LengthFilter()
        with self.assertRaises(ValueError) as ctx:
            f._initialize_by_component_configer(configer)
        self.assertIn('counter', str(ctx.exception))

    def test_initialize_rejects_invalid_drop_mode(self) -> None:
        """An unknown drop_mode value must raise ValueError on init."""
        configer = self._make_configer({'drop_mode': 'drop_all'})
        f = LengthFilter()
        with self.assertRaises(ValueError) as ctx:
            f._initialize_by_component_configer(configer)
        self.assertIn('drop_mode', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
