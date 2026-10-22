# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_boilerplate_remover.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.boilerplate_remover import BoilerplateRemover
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Boilerplate stamped on every page of a corporate report batch.
HEADER = "ACME CONFIDENTIAL - INTERNAL USE ONLY"
FOOTER = "(c) 2026 ACME Corp. All rights reserved."

# Short structural separator line (normalized length 3 < default
# min_line_len of 4) that the safe-list must protect.
SEPARATOR = "---"


def _doc(text, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata.

    None text needs an explicit id: the Document constructor derives ids
    from the text via uuid5, which rejects None.
    """
    if text is None:
        return Document(id="doc-none", text=None,
                        metadata=dict(metadata) or None)
    return Document(text=text, metadata=dict(metadata) or None)


def _batch(n_docs: int, body_prefix: str = "Report section") -> list:
    """Build an n-document batch sharing HEADER/FOOTER/SEPARATOR."""
    docs = []
    for i in range(n_docs):
        docs.append(_doc(
            f"{HEADER}\n"
            f"\n"
            f"{body_prefix} {i}: revenue grew twelve percent year over "
            f"year driven by services demand.\n"
            f"\n"
            f"{SEPARATOR}\n"
            f"\n"
            f"{FOOTER}"
        ))
    return docs


class TestBoilerplateRemover(unittest.TestCase):
    """Comprehensive test suite for BoilerplateRemover."""

    def setUp(self):
        self.remover = BoilerplateRemover()
        self.query = Query(query_str="boilerplate")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        """Defaults: 0.6 fraction, min_docs disabled, remove-lines mode,
        safe-list at 4 characters."""
        r = BoilerplateRemover()
        self.assertEqual(r.threshold, 0.6)
        self.assertIsNone(r.min_docs)
        self.assertEqual(r.mode, "remove-lines")
        self.assertEqual(r.min_line_len, 4)

    def test_initialize_by_component_configer(self):
        """YAML-provided parameters are applied on initialization."""
        configer = self._create_configer({
            'name': 'boilerplate_remover',
            'description': 'strip repeated boilerplate lines',
            'threshold': 0.8,
            'min_docs': 3,
            'mode': 'tag-only',
            'min_line_len': 10,
        })
        r = BoilerplateRemover()
        r._initialize_by_component_configer(configer)
        self.assertEqual(r.threshold, 0.8)
        self.assertEqual(r.min_docs, 3)
        self.assertEqual(r.mode, "tag-only")
        self.assertEqual(r.min_line_len, 10)
        self.assertEqual(r.name, "boilerplate_remover")

    def test_invalid_configuration_raises(self):
        """Out-of-range threshold / min_docs / min_line_len, wrong types,
        bool masquerading as int and unknown modes all fail at load
        time."""
        base = {
            'name': 'r', 'description': 'd',
            'threshold': 0.6, 'min_docs': None,
            'mode': 'remove-lines', 'min_line_len': 4,
        }
        for key, value in (
            ('threshold', 0),
            ('threshold', -0.5),
            ('threshold', 1.01),
            ('threshold', 'high'),
            ('threshold', True),
            ('min_docs', 1),
            ('min_docs', 0),
            ('min_docs', 2.5),
            ('min_docs', True),
            ('mode', 'random'),
            ('mode', ''),
            ('min_line_len', -1),
            ('min_line_len', 1.5),
            ('min_line_len', False),
        ):
            config = dict(base, **{key: value})
            with self.assertRaises(ValueError, msg=f"{key}={value!r}"):
                BoilerplateRemover()._initialize_by_component_configer(
                    self._create_configer(config))

    def test_valid_boundary_configuration_accepted(self):
        """threshold 1.0 and 0.001, min_docs 2 and min_line_len 0 are all
        legal extremes and load without error."""
        configer = self._create_configer({
            'name': 'r', 'description': 'd',
            'threshold': 1.0, 'min_docs': 2,
            'mode': 'remove-lines', 'min_line_len': 0,
        })
        r = BoilerplateRemover()
        r._initialize_by_component_configer(configer)
        self.assertEqual(r.threshold, 1.0)
        self.assertEqual(r.min_docs, 2)
        self.assertEqual(r.min_line_len, 0)

    # ========== Core removal behavior ==========

    def test_shared_header_and_footer_removed_across_batch(self):
        """A header and footer (and the everywhere-repeated separator)
        disappear; the unique body text and the blank lines around it
        survive, so the cleaned text keeps its paragraph shape."""
        docs = _batch(5)
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(len(result), 5)
        for i, doc in enumerate(result):
            self.assertEqual(
                doc.text,
                f"\n"
                f"Report section {i}: revenue grew twelve percent year "
                f"over year driven by services demand.\n"
                f"\n",
                f"document {i} text mismatch")
            self.assertNotIn(HEADER, doc.text)
            self.assertNotIn(FOOTER, doc.text)
            self.assertNotIn(SEPARATOR, doc.text)

    def test_unique_content_preserved(self):
        """Lines appearing in only one document are never touched, even
        when they look like typical boilerplate."""
        unique_line = "Page 3 of 10 - draft circulation only"
        docs = _batch(5)
        docs[2] = _doc(docs[2].text + f"\n{unique_line}")
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            if doc is result[2]:
                self.assertIn(unique_line, doc.text)
            else:
                self.assertNotIn(unique_line, doc.text)

    def test_document_identity_and_order_preserved(self):
        """The same Document objects come back in the same order with
        unchanged ids."""
        docs = _batch(4)
        ids = [d.id for d in docs]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(len(result), 4)
        for original, processed in zip(docs, result):
            self.assertIs(processed, original)
        self.assertEqual([d.id for d in result], ids)

    def test_text_untouched_when_nothing_removed(self):
        """A document without boilerplate keeps its exact original string
        (line endings and trailing newline included) even when other
        documents of the batch were rewritten."""
        dirty = _doc(f"{HEADER}\nshared body line\n{FOOTER}")
        clean_text = "unique one\r\nunique two\r\n"
        clean = _doc(clean_text)
        # HEADER reaches 3/5 documents (0.6, inclusive) and is removed;
        # FOOTER is only in 1/5 and must stay; `clean` shares nothing.
        docs = [dirty, _doc(f"{HEADER}\nother body"), _doc(f"{HEADER}\n"
                "third body"), _doc("fourth body text here"), clean]
        result = self.remover.process_docs(docs, self.query)
        self.assertNotIn(HEADER, result[0].text)
        self.assertEqual(result[0].text, f"shared body line\n{FOOTER}")
        self.assertEqual(result[2].text, "third body")
        self.assertEqual(result[3].text, "fourth body text here")
        self.assertEqual(result[4].text, clean_text)
        self.assertIsNone(result[4].metadata)

    def test_all_lines_boilerplate_yields_empty_text(self):
        """A document consisting entirely of shared lines becomes empty
        text but is still returned (line-level cleanup never drops
        documents)."""
        shared = "ACME CONFIDENTIAL - INTERNAL USE ONLY"
        docs = [_doc(shared), _doc(shared), _doc(shared),
                _doc("unrelated prose that stays")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].text, "")
        self.assertEqual(result[3].text, "unrelated prose that stays")

    # ========== Threshold fraction boundaries ==========

    def test_threshold_fraction_boundaries(self):
        """3 of 5 documents satisfies 0.6 exactly (inclusive boundary);
        2 of 5 does not; threshold 1.0 demands every document."""
        line = "CONFIDENTIAL - DO NOT DISTRIBUTE"
        docs = [_doc("alpha body"), _doc("bravo body"), _doc("charlie"),
                _doc("delta body"), _doc("echo body")]
        for doc in docs[:3]:
            doc.text = f"{line}\n{doc.text}"

        # 3/5 = 0.6 >= 0.6: removed at the default threshold.
        result = self.remover.process_docs(list(docs), self.query)
        for doc in result:
            self.assertNotIn(line, doc.text, "3/5 must satisfy 0.6")

        # 2/5 = 0.4 < 0.6: kept.
        docs2 = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                 _doc("charlie"), _doc("delta"), _doc("echo")]
        result = self.remover.process_docs(docs2, self.query)
        self.assertIn(line, result[0].text)
        self.assertIn(line, result[1].text)

        # threshold 1.0: only lines in every document are removed.
        self.remover.threshold = 1.0
        docs3 = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                 _doc(f"{line}\ncharlie"), _doc("delta"), _doc("echo")]
        result = self.remover.process_docs(docs3, self.query)
        for doc in result[:3]:
            self.assertIn(line, doc.text, "3/5 must not satisfy 1.0")

        docs4 = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                 _doc(f"{line}\ncharlie"), _doc(f"{line}\ndelta"),
                 _doc(f"{line}\necho")]
        result = self.remover.process_docs(docs4, self.query)
        for doc in result:
            self.assertNotIn(line, doc.text, "5/5 must satisfy 1.0")
        self.assertEqual(result[0].text, "alpha")

    def test_threshold_boundary_with_two_thirds(self):
        """2 of 3 documents (0.667) passes 0.6 but fails 0.7. Fresh
        documents are built per pass because removal rewrites text in
        place."""
        line = "INTERNAL MEMORANDUM - FINANCE DIVISION"

        def fresh():
            return [_doc(f"{line}\nfirst"), _doc(f"{line}\nsecond"),
                    _doc("third")]

        result = self.remover.process_docs(fresh(), self.query)
        for doc in result:
            self.assertNotIn(line, doc.text)

        self.remover.threshold = 0.7
        result = self.remover.process_docs(fresh(), self.query)
        self.assertIn(line, result[0].text)
        self.assertIn(line, result[1].text)

    # ========== min_docs absolute-count mode ==========

    def test_min_docs_absolute_count_rule(self):
        """A line in 3 of 5 documents (0.4 fraction) is removed via
        min_docs=3 even though the fraction misses the threshold."""
        line = "DRAFT - NOT FOR DISTRIBUTION"
        docs = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                _doc(f"{line}\ncharlie"), _doc("delta"), _doc("echo")]
        self.remover.min_docs = 3
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            self.assertNotIn(line, doc.text)

    def test_min_docs_and_threshold_combine_with_or(self):
        """min_docs=2 promotes a 2-of-5 line (0.4 fraction) to
        boilerplate: the two rules combine with OR."""
        line = "SUPERSEDED VERSION"
        docs = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                _doc("charlie"), _doc("delta"), _doc("echo")]
        self.remover.min_docs = 2
        result = self.remover.process_docs(docs, self.query)
        self.assertNotIn(line, result[0].text)
        self.assertNotIn(line, result[1].text)

    def test_min_docs_above_batch_size(self):
        """min_docs larger than the batch is simply unreachable; the
        fraction rule alone decides (the line stays in its 2/5 docs)."""
        line = "RARE HEADER LINE"
        docs = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
                _doc("charlie"), _doc("delta"), _doc("echo")]
        self.remover.min_docs = 10
        result = self.remover.process_docs(docs, self.query)
        self.assertIn(line, result[0].text)
        self.assertIn(line, result[1].text)

    # ========== tag-only mode ==========

    def test_tag_only_mode_leaves_text_untouched(self):
        """tag-only records the findings in metadata['boilerplate_lines']
        without touching the text; every line detected by the batch
        analysis (header, everywhere-repeated separator, footer) is
        listed in document order."""
        self.remover.mode = "tag-only"
        docs = _batch(3)
        originals = [d.text for d in docs]
        result = self.remover.process_docs(docs, self.query)
        for original, doc in zip(originals, result):
            self.assertEqual(doc.text, original)
            self.assertIn(HEADER, doc.text)
            self.assertEqual(
                doc.metadata["boilerplate_lines"],
                [HEADER, SEPARATOR,
                 "(c) 2026 ACME Corp. All rights reserved."])
            self.assertEqual(doc.metadata["boilerplate_removed_count"], 3)
            self.assertEqual(doc.metadata["boilerplate_sample"],
                             [HEADER, SEPARATOR,
                              "(c) 2026 ACME Corp. All rights reserved."])
        # Exactly the three bookkeeping keys are stamped, nothing else.
        self.assertEqual(
            set(result[0].metadata),
            {"boilerplate_removed_count", "boilerplate_sample",
             "boilerplate_lines"})

    def test_tag_only_matches_remove_lines_findings(self):
        """Both modes agree on what is boilerplate: the lines removed in
        remove-lines mode are exactly the lines listed in tag-only
        mode. Fresh document objects are used per mode because
        remove-lines mutates the text in place."""
        line = "REPEATED DISCLAIMER TEXT"

        self.remover.mode = "remove-lines"
        removed_mode = self.remover.process_docs(
            [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
             _doc(f"{line}\ncharlie")], self.query)
        self.assertEqual(removed_mode[0].text, "alpha")

        self.remover.mode = "tag-only"
        tagged_mode = self.remover.process_docs(
            [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo"),
             _doc(f"{line}\ncharlie")], self.query)
        self.assertEqual(tagged_mode[0].metadata["boilerplate_lines"],
                         [line])

    # ========== min_line_len safe-list ==========

    def test_short_line_safe_list_protected_below_threshold(self):
        """A 3-character separator in 4 of 5 documents (0.8 fraction) is
        NOT removed: short lines need every-document evidence."""
        self.assertEqual(len(SEPARATOR), 3)
        self.assertLess(len(SEPARATOR), self.remover.min_line_len)
        docs = [_doc(f"{SEPARATOR}\nalpha"), _doc(f"{SEPARATOR}\nbravo"),
                _doc(f"{SEPARATOR}\ncharlie"), _doc(f"{SEPARATOR}\ndelta"),
                _doc("echo")]
        result = self.remover.process_docs(docs, self.query)
        for doc in result[:4]:
            self.assertIn(SEPARATOR, doc.text)

    def test_short_line_removed_when_in_every_document(self):
        """The same short separator IS removed when it appears in every
        document of the batch."""
        docs = [_doc(f"{SEPARATOR}\nalpha"), _doc(f"{SEPARATOR}\nbravo"),
                _doc(f"{SEPARATOR}\ncharlie"), _doc(f"{SEPARATOR}\ndelta"),
                _doc(f"{SEPARATOR}\necho")]
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            self.assertNotIn(SEPARATOR, doc.text)
        self.assertEqual(result[0].text, "alpha")

    def test_long_line_removed_at_same_frequency(self):
        """A line at/above min_line_len in 4 of 5 documents IS removed at
        the default 0.6 threshold, proving the safe-list (not the
        fraction) protected the short line."""
        long_line = "SECTION BREAK MARKER FORTY-TWO"
        docs = [_doc(f"{long_line}\nalpha"),
                _doc(f"{long_line}\nbravo"),
                _doc(f"{long_line}\ncharlie"),
                _doc(f"{long_line}\ndelta"),
                _doc("echo")]
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            self.assertNotIn(long_line, doc.text)

    def test_min_line_len_zero_disables_safe_list(self):
        """min_line_len=0 lets the 3-character separator in 4 of 5
        documents be removed by the fraction rule."""
        self.remover.min_line_len = 0
        docs = [_doc(f"{SEPARATOR}\nalpha"), _doc(f"{SEPARATOR}\nbravo"),
                _doc(f"{SEPARATOR}\ncharlie"), _doc(f"{SEPARATOR}\ndelta"),
                _doc("echo")]
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            self.assertNotIn(SEPARATOR, doc.text)

    def test_min_line_len_measured_on_normalized_line(self):
        """The safe-list compares the length of the NORMALIZED line: a
        line padded with whitespace beyond min_line_len is treated as
        long even though its raw form is longer still."""
        padded = "  " + SEPARATOR + " x"  # normalized: "--- x" (5 chars)
        self.assertGreaterEqual(len(" ".join(padded.split())),
                                self.remover.min_line_len)
        docs = [_doc(f"{padded}\nalpha"), _doc(f"{padded}\nbravo"),
                _doc(f"{padded}\ncharlie"), _doc(f"{padded}\ndelta"),
                _doc("echo")]
        result = self.remover.process_docs(docs, self.query)
        for doc in result:
            self.assertNotIn(padded, doc.text)

    # ========== Single-document and empty batches ==========

    def test_single_document_batch_no_removal(self):
        """A lone document passes through untouched: repetition needs
        cross-document evidence, so even a threshold of 0.001 removes
        nothing and stamps nothing."""
        self.remover.threshold = 0.001
        text = f"{HEADER}\n\nbody\n\n{FOOTER}"
        doc = _doc(text, source="wire")
        result = self.remover.process_docs([doc], self.query)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, text)
        self.assertEqual(doc.metadata, {"source": "wire"})

    def test_two_document_batch_has_enough_evidence(self):
        """Two documents sharing a line DO provide cross-document
        evidence: 2/2 = 1.0 satisfies the default threshold."""
        line = "SHARED EMAIL SIGNATURE BLOCK"
        docs = [_doc(f"{line}\nalpha"), _doc(f"{line}\nbravo")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(result[0].text, "alpha")
        self.assertEqual(result[1].text, "bravo")

    def test_empty_batch(self):
        """An empty batch yields an empty list."""
        self.assertEqual(self.remover.process_docs([], self.query), [])

    def test_none_and_empty_text_documents(self):
        """None/empty-text documents contribute no lines but still count
        in the fraction denominator; they pass through with no
        stamps."""
        shared = "REPEATED HEADER LINE"
        docs = [_doc(None), _doc(""), _doc(f"{shared}\nalpha"),
                _doc(f"{shared}\nbravo"), _doc(f"{shared}\ncharlie")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(len(result), 5)
        # 3 of 5 documents carry the line: 0.6, removed.
        self.assertEqual(result[2].text, "alpha")
        # The empty documents were neither rewritten nor stamped.
        self.assertIsNone(result[0].text)
        self.assertEqual(result[1].text, "")
        self.assertIsNone(result[0].metadata)
        self.assertIsNone(result[1].metadata)

    def test_all_empty_documents_batch(self):
        """A batch of empty documents changes nothing and stamps
        nothing."""
        docs = [_doc(None), _doc(""), _doc("   ")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual([d.text for d in result], [None, "", "   "])
        for doc in result:
            self.assertIsNone(doc.metadata)

    # ========== Normalization semantics ==========

    def test_whitespace_normalization_merges_lines(self):
        """Differently indented/padded copies of the same header count as
        one line; the sample records the normalized form."""
        variants = [
            "ACME Corp  Annual Report 2026",
            "  ACME Corp Annual  Report 2026  ",
            "\tACME Corp Annual Report 2026",
            "ACME Corp Annual Report 2026",
        ]
        docs = [_doc(f"{variant}\nbody {i}")
                for i, variant in enumerate(variants)]
        docs.append(_doc("unrelated echo document"))
        result = self.remover.process_docs(docs, self.query)
        for i, doc in enumerate(result[:4]):
            self.assertNotIn(variants[0], doc.text, f"doc {i}")
            self.assertTrue(doc.text.startswith("body"), f"doc {i}")
        self.assertEqual(result[0].metadata["boilerplate_sample"],
                         ["ACME Corp Annual Report 2026"])

    def test_same_line_twice_in_one_document_counts_once(self):
        """A header printed twice within one document counts once for
        that document: twice-in-doc-0 plus docs 1 and 2 gives 3/5, which
        satisfies 0.6 and removes BOTH occurrences in document 0."""
        line = "DAILY STANDUP NOTES"
        docs = [_doc(f"{line}\nfirst\n{line}\npara"), _doc(f"{line}\nsecond"),
                _doc(f"{line}\nthird"), _doc("fourth"), _doc("fifth")]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(result[0].text, "first\npara")
        self.assertEqual(result[1].text, "second")
        self.assertEqual(result[3].text, "fourth")

    def test_case_is_not_folded(self):
        """'CONFIDENTIAL' and 'Confidential' are distinct normalized
        lines: 3+3 of 6 documents stays below 0.6 each, so nothing is
        removed (a case-folding implementation would see 6/6)."""
        upper = "CONFIDENTIAL MEMO LINE"
        lower = "confidential memo line"
        docs = [_doc(f"{upper}\n{i}") for i in range(3)] + \
               [_doc(f"{lower}\n{i}") for i in range(3)]
        result = self.remover.process_docs(docs, self.query)
        for i, doc in enumerate(result):
            self.assertIn(upper if i < 3 else lower, doc.text)

    # ========== Metadata bookkeeping ==========

    def test_metadata_counts_and_sample_capped_at_five(self):
        """removed_count counts every removed line of the document;
        sample keeps only the first 5, in document order."""
        lines = [f"BOILERPLATE LINE NUMBER {i:02d}" for i in range(7)]
        text = "\n".join(lines) + "\nreal content stays"
        docs = [_doc(text)] + [_doc("\n".join(lines))]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(result[0].metadata["boilerplate_removed_count"], 7)
        self.assertEqual(result[0].metadata["boilerplate_sample"], lines[:5])
        self.assertEqual(result[0].text, "real content stays")
        self.assertEqual(result[1].metadata["boilerplate_removed_count"], 7)
        self.assertEqual(result[1].text, "")

    def test_documents_without_boilerplate_not_stamped(self):
        """Only documents that actually lost (or tagged) lines receive
        the metadata; clean documents keep their metadata mapping
        untouched."""
        shared = "COMMON DISCLAIMER LINE"
        clean = _doc("fully unique text", source="wire")
        docs = [_doc(f"{shared}\nalpha"), _doc(f"{shared}\nbravo"), clean]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(clean.metadata, {"source": "wire"})
        self.assertNotIn("boilerplate_removed_count", clean.metadata)
        self.assertEqual(result[0].metadata["boilerplate_removed_count"], 1)

    def test_existing_metadata_preserved_and_copied(self):
        """Pre-existing metadata entries survive stamping, and stamps go
        through a copied mapping: the caller's original dict never gains
        keys in place."""
        shared = "COMMON DISCLAIMER LINE"
        doc = _doc(f"{shared}\nalpha", source="wire", rank=1)
        meta_ref = doc.metadata
        result = self.remover.process_docs([doc, _doc(f"{shared}\nbeta")],
                                           self.query)
        self.assertEqual(result[0].metadata["source"], "wire")
        self.assertEqual(result[0].metadata["rank"], 1)
        self.assertEqual(result[0].metadata["boilerplate_removed_count"], 1)
        self.assertNotIn("boilerplate_removed_count", meta_ref)
        self.assertIsNot(doc.metadata, meta_ref)

    # ========== Pipeline-shape tests ==========

    def test_query_argument_accepted(self):
        """process_docs accepts a Query like any other doc processor; the
        result does not depend on it."""
        docs = _batch(3)
        with_query = self.remover.process_docs(_batch(3),
                                               Query(query_str="audit"))
        without_query = self.remover.process_docs(_batch(3))
        self.assertEqual([d.text for d in with_query],
                         [d.text for d in without_query])
        self.assertNotIn(HEADER, with_query[0].text)

    def test_remove_lines_drops_only_boilerplate_occurrences(self):
        """Every occurrence of a boilerplate line is dropped and all
        other lines survive verbatim, in order, joined by newlines."""
        boiler = "REPEATED EVERYWHERE LINE"
        docs = [
            _doc(f"first\n{boiler}\nmiddle\n{boiler}\nlast"),
            _doc(f"{boiler}\nhead\n{boiler}"),
            _doc(f"{boiler}\n{boiler}\nsolo"),
        ]
        result = self.remover.process_docs(docs, self.query)
        self.assertEqual(result[0].text, "first\nmiddle\nlast")
        self.assertEqual(result[1].text, "head")
        self.assertEqual(result[2].text, "solo")


if __name__ == '__main__':
    unittest.main()
