# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_contact_entity_extractor.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.contact_entity_extractor import ContactEntityExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# A business-notice paragraph with a known set of contact entities.
# Ground truth (default config, dedupe on):
#   email -> Sales@acme-parts.example.com, old.acct@mail.acme-parts.example
#   url   -> https://portal.acme-parts.example/orders?id=7,
#            www.acme-parts.example/docs
#   phone -> +86 571 8888 6666, (555) 123-4567, 13800138000
# ('555-123-4567' dedupes into '(555) 123-4567' digit-wise.)
BIZ_TEXT = (
    "Supplier: Hangzhou Acme Parts Co., Ltd. Reach us via "
    "Sales@acme-parts.example.com or the legacy mailbox "
    "old.acct@mail.acme-parts.example; urgent line +86 571 8888 6666. "
    "Portal: https://portal.acme-parts.example/orders?id=7, docs at "
    "www.acme-parts.example/docs. US office: (555) 123-4567, alternate "
    "555-123-4567. Mobile 13800138000."
)

BIZ_TRUTH = {
    "email": ["Sales@acme-parts.example.com",
              "old.acct@mail.acme-parts.example"],
    "url": ["https://portal.acme-parts.example/orders?id=7",
            "www.acme-parts.example/docs"],
    "phone": ["+86 571 8888 6666", "(555) 123-4567", "13800138000"],
}

# Chinese supply-chain notice: no spaces around punctuation, full-width
# separators, URL glued to a following sentence.
ZH_TEXT = ("供应商：张伟，邮箱 zhang.wei@supplier.cn，电话13800138000，"
           "官网 https://www.gongying.cn/products。")

ZH_TRUTH = {
    "email": ["zhang.wei@supplier.cn"],
    "url": ["https://www.gongying.cn/products"],
    "phone": ["13800138000"],
}

# Lookalikes that must NOT be extracted: long digit runs, a bare 10-digit
# order id, an address without a TLD, a bare domain mention, an IPv4, a
# date and a version number.
PRECISION_TEXT = ("Refs 12345678901234 and order 5551234567 and foo@bar "
                  "and @example.com and 999.999.999.999 and date 2026-10-19 "
                  "and version 1.234.5678x.")


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestContactEntityExtractor(unittest.TestCase):
    """Comprehensive test suite for ContactEntityExtractor."""

    def setUp(self):
        self.extractor = ContactEntityExtractor()
        self.query = Query(query_str="contacts")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: all three kinds, 'entities' / 'entity_counts' keys,
        dedupe on, unlimited per kind."""
        e = ContactEntityExtractor()
        self.assertEqual(e.entity_types, ["email", "url", "phone"])
        self.assertEqual(e.entities_key, "entities")
        self.assertEqual(e.counts_key, "entity_counts")
        self.assertTrue(e.dedupe)
        self.assertEqual(e.max_per_type, 0)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'contact_entity_extractor',
            'description': 'contact entity extractor',
            'entity_types': ['email', 'phone'],
            'entities_key': 'contacts',
            'counts_key': 'contact_counts',
            'dedupe': False,
            'max_per_type': 5,
        })
        e = ContactEntityExtractor()
        e._initialize_by_component_configer(configer)
        self.assertEqual(e.entity_types, ["email", "phone"])
        self.assertEqual(e.entities_key, "contacts")
        self.assertEqual(e.counts_key, "contact_counts")
        self.assertFalse(e.dedupe)
        self.assertEqual(e.max_per_type, 5)
        self.assertEqual(e.name, "contact_entity_extractor")

    def test_invalid_configuration_raises(self):
        """Unknown kinds, empty or malformed entity_types, non-string
        metadata keys and bad max_per_type all fail at load time."""
        base = {
            'name': 'e', 'description': 'd',
            'entity_types': ['email'], 'entities_key': 'entities',
            'counts_key': 'entity_counts', 'dedupe': True,
            'max_per_type': 0,
        }
        for key, value in (
            ('entity_types', ['email', 'fax']),
            ('entity_types', []),
            ('entity_types', 'email'),
            ('entity_types', ['email', 7]),
            ('entities_key', 5),
            ('counts_key', ['x']),
            ('max_per_type', -1),
            ('max_per_type', 2.5),
            ('max_per_type', True),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                ContactEntityExtractor()._initialize_by_component_configer(
                    self._create_configer(config))

    # ========== Pattern ground-truth tests ==========

    def test_business_text_ground_truth(self):
        """Every kind is extracted exactly, in first-occurrence order,
        with sentence punctuation trimmed and the duplicate phone
        collapsed."""
        doc = _doc(BIZ_TEXT)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["entities"], BIZ_TRUTH)
        self.assertEqual(result[0].metadata["entity_counts"],
                         {"email": 2, "url": 2, "phone": 3})

    def test_chinese_text_ground_truth(self):
        """CJK prose works without segmentation: full-width punctuation
        ends entities cleanly and the URL does not swallow the sentence
        after it."""
        doc = _doc(ZH_TEXT)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["entities"], ZH_TRUTH)

    def test_lookalikes_not_extracted(self):
        """Long digit runs, bare 10-digit ids, TLD-less addresses, bare
        domain mentions, IPv4, dates and versions are not entities."""
        doc = _doc(PRECISION_TEXT)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["entities"],
                         {"email": [], "url": [], "phone": []})
        self.assertEqual(result[0].metadata["entity_counts"],
                         {"email": 0, "url": 0, "phone": 0})

    def test_email_shape_variants(self):
        """Plus-tagged local parts, mixed case, subdomains and numeric
        TLD-less hosts; addresses without a letter TLD stay out."""
        text = ("a b+tag@sub.deep.example.co.uk c "
                "UPPER@EXAMPLE.COM d host@127.0.0.1 e")
        self.assertEqual(self.extractor._extract(text, "email"),
                         ["b+tag@sub.deep.example.co.uk",
                          "UPPER@EXAMPLE.COM"])

    def test_url_shape_variants(self):
        """Ports and queries kept; balanced trailing ')' inside a path
        kept, prose-wrapped ')' dropped, trailing '.' dropped."""
        text = ("(see https://example.com/path) plus "
                "https://en.wikipedia.org/wiki/Python_(programming_language) "
                "and http://host.example:8080/a/b?x=1,y=2.")
        self.assertEqual(self.extractor._extract(text, "url"),
                         ["https://example.com/path",
                          "https://en.wikipedia.org/wiki/"
                          "Python_(programming_language)",
                          "http://host.example:8080/a/b?x=1,y=2"])

    def test_phone_shape_variants(self):
        """China mobile, NANP paren/dot/space forms and leading-plus
        international forms all match; a bare 10-digit run does not.
        (Each number is distinct so dedupe keeps them all.)"""
        text = ("call 13800138000 or (555) 123-4567 or 212.555.0166 or "
                "303 555 0177 or +1-800-555-0199 but not 5551234567 ok")
        self.assertEqual(self.extractor._extract(text, "phone"),
                         ["13800138000", "(555) 123-4567",
                          "212.555.0166", "303 555 0177",
                          "+1-800-555-0199"])

    # ========== Helper unit tests ==========

    def test_trim_strips_punctuation_and_unbalanced_brackets(self):
        """Sentence punctuation (ASCII and full-width) is removed; a
        closing bracket is removed only when unbalanced within the
        match."""
        trim = ContactEntityExtractor._trim
        self.assertEqual(trim("https://example.com."), "https://example.com")
        self.assertEqual(trim("a@b.example,"), "a@b.example")
        self.assertEqual(trim("www.x.example。"), "www.x.example")
        # Unbalanced closer dropped — the prose-wrapped URL case, where
        # the regex match starts after the opening bracket.
        self.assertEqual(trim("https://example.com/path)"),
                         "https://example.com/path")
        # Balanced closer kept — the Wikipedia-style path case.
        self.assertEqual(trim("wiki_(python)"), "wiki_(python)")
        self.assertEqual(trim("(see x)"), "(see x)")
        self.assertEqual(trim("path])"), "path")
        self.assertEqual(trim("..."), "")

    def test_identity_normalizes_for_comparison(self):
        """Emails/URLs compare case-folded; phones compare digit-wise."""
        identity = ContactEntityExtractor._identity
        self.assertEqual(identity("A@B.example", "email"),
                         identity("a@b.EXAMPLE", "email"))
        self.assertEqual(identity("https://X.example", "url"),
                         identity("https://x.example", "url"))
        self.assertNotEqual(identity("a@b.example", "email"),
                            identity("c@b.example", "email"))
        self.assertEqual(identity("(555) 123-4567", "phone"),
                         identity("555-123-4567", "phone"))
        self.assertNotEqual(identity("5551234567", "phone"),
                            identity("5551234568", "phone"))

    # ========== Behavior tests ==========

    def test_dedupe_keeps_first_spelling(self):
        """Case-variant emails collapse to the first spelling; phone
        separator variants collapse digit-wise; order is first
        occurrence."""
        text = ("mail A@x.example then a@x.example then B@x.example, "
                "call 555-123-4567 or (555) 123-4567")
        self.assertEqual(self.extractor._extract(text, "email"),
                         ["A@x.example", "B@x.example"])
        self.assertEqual(self.extractor._extract(text, "phone"),
                         ["555-123-4567"])

    def test_dedupe_disabled_keeps_every_occurrence(self):
        """With dedupe=False duplicates stay, in text order."""
        self.extractor.dedupe = False
        text = "A@x.example and a@x.example and A@x.example"
        self.assertEqual(self.extractor._extract(text, "email"),
                         ["A@x.example", "a@x.example", "A@x.example"])

    def test_max_per_type_caps_each_kind_independently(self):
        """The cap keeps the earliest values per kind and applies after
        dedupe; 0 means unlimited."""
        self.extractor.max_per_type = 1
        doc = _doc(BIZ_TEXT)
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["entities"],
                         {"email": ["Sales@acme-parts.example.com"],
                          "url": ["https://portal.acme-parts.example/orders?id=7"],
                          "phone": ["+86 571 8888 6666"]})
        self.assertEqual(result[0].metadata["entity_counts"],
                         {"email": 1, "url": 1, "phone": 1})

    def test_entity_types_subset_extracts_only_enabled_kinds(self):
        """A subset stamps only those kinds, in the configured order,
        and ignores everything else in the text."""
        self.extractor.entity_types = ["phone", "email"]
        doc = _doc(BIZ_TEXT)
        result = self.extractor.process_docs([doc], self.query)
        entities = result[0].metadata["entities"]
        self.assertEqual(list(entities.keys()), ["phone", "email"])
        self.assertEqual(entities["phone"], BIZ_TRUTH["phone"])
        self.assertEqual(entities["email"], BIZ_TRUTH["email"])
        self.assertNotIn("url", entities)
        self.assertEqual(result[0].metadata["entity_counts"],
                         {"phone": 3, "email": 2})

    # ========== Metadata bookkeeping tests ==========

    def test_all_documents_kept_in_order_and_untouched(self):
        """Extraction adds structure but never filters: every document
        survives, order and text/id are preserved, and a document
        without entities is stamped with empty lists."""
        plain = _doc("no contact details in this paragraph at all")
        docs = [_doc(BIZ_TEXT), plain, _doc(ZH_TEXT)]
        result = self.extractor.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result],
                         [BIZ_TEXT, plain.text, ZH_TEXT])
        self.assertEqual([d.id for d in result], [d.id for d in docs])
        self.assertEqual(plain.metadata["entities"],
                         {"email": [], "url": [], "phone": []})

    def test_metadata_preserved_and_copied_before_mutation(self):
        """Pre-existing metadata entries survive; stamping writes through
        a copy, so the caller's original mapping is never mutated in
        place."""
        doc = _doc(BIZ_TEXT, source="crm", rank=3)
        meta_ref = doc.metadata
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["source"], "crm")
        self.assertEqual(result[0].metadata["rank"], 3)
        self.assertNotIn("entities", meta_ref)
        self.assertNotIn("entity_counts", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    def test_disabled_keys_stamp_nothing(self):
        """Empty entities_key / counts_key disable both stamps; existing
        metadata stays exactly as it was."""
        self.extractor.entities_key = ""
        self.extractor.counts_key = ""
        doc = _doc(BIZ_TEXT, source="crm")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata, {"source": "crm"})

    def test_empty_and_none_text_tolerated(self):
        """Empty batch yields empty output; empty and None texts are
        stamped with empty lists rather than raising."""
        self.assertEqual(self.extractor.process_docs([], self.query), [])
        blank = _doc("")
        result = self.extractor.process_docs([blank], self.query)
        self.assertEqual(result[0].metadata["entities"],
                         {"email": [], "url": [], "phone": []})

    def test_deterministic_across_instances_and_runs(self):
        """Identical inputs produce identical metadata on fresh
        instances and repeated runs — the output is byte-stable."""
        first = _doc(BIZ_TEXT)
        self.extractor.process_docs([first], self.query)
        second = _doc(BIZ_TEXT)
        ContactEntityExtractor().process_docs([second], self.query)
        self.assertEqual(first.metadata, second.metadata)
        again = _doc(BIZ_TEXT)
        self.extractor.process_docs([again], self.query)
        self.assertEqual(first.metadata, again.metadata)


if __name__ == '__main__':
    unittest.main()
