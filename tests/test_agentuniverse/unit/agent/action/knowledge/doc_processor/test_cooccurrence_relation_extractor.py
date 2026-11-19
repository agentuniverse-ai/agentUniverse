# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_cooccurrence_relation_extractor.py

import os
import unittest

import yaml

from agentuniverse.agent.action.knowledge.doc_processor.cooccurrence_relation_extractor import \
    CooccurrenceRelationExtractor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

# Ground-truth corpus: three sentences, three tracked companies. Each of
# the three pairs shares exactly one sentence.
GROUND_TRUTH_TEXT = (
    "Apple supplies display panels to Samsung. "
    "Samsung and Taiwan Semiconductor announced a joint venture. "
    "Apple doubled its orders from Taiwan Semiconductor last year."
)

# Repository root, seven levels above this test file.
_REPO_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir,
    os.pardir))


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


def _relations(extractor: CooccurrenceRelationExtractor, text: str):
    """Run the extractor over one document and return its metadata."""
    doc = _doc(text)
    result = extractor.process_docs([doc], Query(query_str="graph"))
    return result[0].metadata


class TestCooccurrenceRelationExtractor(unittest.TestCase):
    """Comprehensive test suite for CooccurrenceRelationExtractor."""

    def setUp(self):
        self.extractor = CooccurrenceRelationExtractor()
        self.query = Query(query_str="co-occurrence")

    def _create_configer(self, config_dict) -> ComponentConfiger:
        """Create a ComponentConfiger from a plain dictionary.

        Component name/description defaults are injected because the
        DocProcessor base initializer reads them unconditionally.
        """
        merged = {"name": "test_extractor", "description": "test"}
        merged.update(config_dict)
        cfg = Configer()
        cfg.value = merged
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    # ========== Extraction: ground truth ==========

    def test_ground_truth_pairs_and_counts(self):
        """Three sentences over three terms yield the three known pairs."""
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Taiwan Semiconductor"])
        meta = _relations(ext, GROUND_TRUTH_TEXT)
        self.assertEqual(meta["relations"], [
            {"source": "Apple", "target": "Samsung", "count": 1},
            {"source": "Apple", "target": "Taiwan Semiconductor", "count": 1},
            {"source": "Samsung", "target": "Taiwan Semiconductor", "count": 1},
        ])
        self.assertEqual(meta["relation_graph"], {
            "Apple": {"Samsung": 1, "Taiwan Semiconductor": 1},
            "Samsung": {"Apple": 1, "Taiwan Semiconductor": 1},
            "Taiwan Semiconductor": {"Apple": 1, "Samsung": 1},
        })

    def test_counts_accumulate_across_sentences(self):
        """A pair co-occurring in three sentences is counted thrice."""
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Nvidia"])
        text = ("Apple met Samsung on Monday. "
                "Nvidia watched Apple and Samsung. "
                "Apple and Samsung met again on Friday.")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"], [
            {"source": "Apple", "target": "Samsung", "count": 3},
            {"source": "Apple", "target": "Nvidia", "count": 1},
            {"source": "Nvidia", "target": "Samsung", "count": 1},
        ])
        self.assertEqual(meta["relation_graph"]["Apple"]["Samsung"], 3)

    def test_pair_counted_once_per_sentence(self):
        """Repetitions inside one window never inflate the pair count."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        text = "Apple met Apple and Samsung about Samsung in Apple's office."
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 1}])

    def test_no_self_relations(self):
        """A term never co-occurs with itself."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        meta = _relations(ext, "Apple Apple Apple. Nothing else here.")
        self.assertEqual(meta["relations"], [])
        self.assertEqual(meta["relation_graph"], {})

    def test_no_relations_when_no_term_present(self):
        """A document without tracked terms is stamped empty, not skipped."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        meta = _relations(ext, "The orchard sold pears and plums at market.")
        self.assertEqual(meta["relations"], [])
        self.assertEqual(meta["relation_graph"], {})

    def test_empty_batch_and_empty_text(self):
        """Empty batches and blank documents are handled gracefully."""
        self.assertEqual(self.extractor.process_docs([]), [])
        ext = CooccurrenceRelationExtractor(terms=["Apple"])
        meta = _relations(ext, "")
        self.assertEqual(meta["relations"], [])
        self.assertEqual(meta["relation_graph"], {})

    # ========== Term matching ==========

    def test_term_matching_is_boundary_aware(self):
        """'Apple' matches neither 'Pineapple' nor plural 'Apples'."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        meta = _relations(ext,
                          "The pineapple stall also sold apples, not Samsung.")
        self.assertEqual(meta["relations"], [])

    def test_term_matching_case_insensitive_with_punctuation(self):
        """Terms match across case and adjacent punctuation."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "samsung"])
        meta = _relations(ext, "apple, SAMSUNG! and (apple) met.")
        self.assertEqual(meta["relations"],
                         [{"source": "Apple", "target": "samsung", "count": 1}])

    def test_alias_canonicalization(self):
        """Aliases fold onto their canonical target before pairing."""
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung"],
            alias_map={"AAPL": "Apple", "苹果": "Apple"})
        text = ("AAPL met Samsung in May. "
                "苹果 signed with Samsung in June.")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 2}])

    def test_alias_overrides_colliding_term(self):
        """An explicit alias wins over a colliding terms entry."""
        ext = CooccurrenceRelationExtractor(
            terms=["AAPL", "Samsung"], alias_map={"AAPL": "Apple"})
        meta = _relations(ext, "AAPL met Samsung.")
        # Canonical 'Apple' proves the alias took precedence over the
        # identity mapping of the 'AAPL' terms entry.
        self.assertEqual(meta["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 1}])

    # ========== Sentence segmentation ==========

    def test_abbreviation_guard_keeps_company_suffix(self):
        """A period after 'Inc.' does not split the sentence."""
        ext = CooccurrenceRelationExtractor(terms=["Boeing", "Airbus"])
        text = ("Boeing Inc. announced a deal with Airbus. "
                "Boeing and Airbus clashed before.")
        meta = _relations(ext, text)
        # With the guard both sentences hold both terms -> count 2. A
        # broken guard would split the first sentence and drop to 1.
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing", "count": 2}])

    def test_initials_guard(self):
        """Periods inside 'J. P. Morgan' do not split the sentence."""
        ext = CooccurrenceRelationExtractor(terms=["J. P. Morgan", "Airbus"])
        meta = _relations(ext, "J. P. Morgan funded Airbus.")
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "J. P. Morgan",
                           "count": 1}])

    def test_decimal_guard(self):
        """A decimal point does not split a sentence."""
        ext = CooccurrenceRelationExtractor(terms=["Boeing", "Airbus"])
        meta = _relations(ext, "Boeing grew 3.5 percent while Airbus fell.")
        # A broken guard would split at "3." and separate the pair.
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing", "count": 1}])

    def test_ellipsis_guard(self):
        """Periods inside an ellipsis do not create sentence windows."""
        ext = CooccurrenceRelationExtractor(terms=["Boeing", "Airbus"])
        meta = _relations(ext, "Boeing waited... Airbus left.")
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing", "count": 1}])

    def test_cjk_sentence_boundaries(self):
        """CJK terminators split sentences for Chinese corpora."""
        ext = CooccurrenceRelationExtractor(terms=["华为", "台积电", "中兴"])
        text = ("华为与台积电签署了合作协议。"
                "中兴与华为展开合作！"
                "台积电单独发布了公告？华为和台积电再次会面。")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"], [
            {"source": "华为", "target": "台积电", "count": 2},
            {"source": "中兴", "target": "华为", "count": 1},
        ])

    def test_cjk_terms_cooccur_without_spaces(self):
        """CJK terms are detected without any whitespace boundaries."""
        ext = CooccurrenceRelationExtractor(terms=["华为", "台积电"])
        meta = _relations(ext, "华为与台积电合作。")
        self.assertEqual(meta["relations"],
                         [{"source": "华为", "target": "台积电", "count": 1}])

    # ========== Window variants ==========

    def test_paragraph_window_spans_sentences(self):
        """window='paragraph' pairs terms across sentences of one block."""
        text = "Apple met Samsung.\n\nSamsung led the region. Nvidia followed."
        sentence_ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Nvidia"], window="sentence")
        meta = _relations(sentence_ext, text)
        self.assertEqual(meta["relations"], [
            {"source": "Apple", "target": "Samsung", "count": 1}])

        paragraph_ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Nvidia"], window="paragraph")
        meta = _relations(paragraph_ext, text)
        self.assertEqual(meta["relations"], [
            {"source": "Apple", "target": "Samsung", "count": 1},
            {"source": "Nvidia", "target": "Samsung", "count": 1},
        ])

    # ========== Filters and ordering ==========

    def test_min_count_filters_weak_pairs(self):
        """Pairs below min_count vanish from both list and graph."""
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Nvidia"], min_count=2)
        text = ("Apple met Samsung on Monday. "
                "Nvidia joined late. "
                "Apple and Samsung met again on Friday.")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 2}])
        self.assertEqual(meta["relation_graph"],
                         {"Apple": {"Samsung": 2}, "Samsung": {"Apple": 2}})

    def test_max_relations_cap_and_tie_ordering(self):
        """The list is capped; ties order alphabetically; graph is not."""
        terms = ["Acme", "Beta", "Cedar", "Delta", "Echo", "Fjord"]
        ext = CooccurrenceRelationExtractor(terms=terms, max_relations=5)
        meta = _relations(ext, "Acme Beta Cedar Delta Echo Fjord gathered.")
        self.assertEqual(meta["relations"], [
            {"source": "Acme", "target": "Beta", "count": 1},
            {"source": "Acme", "target": "Cedar", "count": 1},
            {"source": "Acme", "target": "Delta", "count": 1},
            {"source": "Acme", "target": "Echo", "count": 1},
            {"source": "Acme", "target": "Fjord", "count": 1},
        ])
        # 6 terms all-pairs = 15 relations survive in the adjacency.
        pair_total = sum(len(adj) for adj in meta["relation_graph"].values())
        self.assertEqual(pair_total, 2 * 15)
        self.assertIn("Fjord", meta["relation_graph"]["Beta"])

    def test_count_descends_before_names(self):
        """Higher counts come first regardless of alphabetical order."""
        ext = CooccurrenceRelationExtractor(terms=["Zeta", "Alpha", "Mid"])
        text = ("Zeta and Alpha met. Zeta and Alpha met again. "
                "Mid joined Zeta once. Mid joined Alpha once.")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"][0],
                         {"source": "Alpha", "target": "Zeta", "count": 2})
        self.assertEqual([r["count"] for r in meta["relations"]],
                         [2, 1, 1])

    # ========== Auto-capitalized detection ==========

    def test_auto_capitalized_with_stoplist(self):
        """Capitalized sequences are detected; stoplist words trimmed."""
        ext = CooccurrenceRelationExtractor(auto_capitalized=True)
        text = ("The Boeing Company signed with Airbus. "
                "We also saw Fidelity meet Goldman Sachs. "
                "The meeting ended.")
        meta = _relations(ext, text)
        self.assertEqual(meta["relations"], [
            {"source": "Airbus", "target": "Boeing Company", "count": 1},
            {"source": "Fidelity", "target": "Goldman Sachs", "count": 1},
        ])

    def test_auto_capitalized_possessive_and_periods(self):
        """Trailing possessives and sentence periods are stripped."""
        ext = CooccurrenceRelationExtractor(auto_capitalized=True)
        meta = _relations(ext,
                          "Apple's suppliers include TSMC. "
                          "The U.S. Army bought chips from Oki.")
        self.assertEqual(meta["relations"], [
            {"source": "Apple", "target": "TSMC", "count": 1},
            {"source": "Oki", "target": "U.S. Army", "count": 1},
        ])

    def test_auto_capitalized_no_gluing_across_periods(self):
        """A sentence-final period never glues names across sentences."""
        ext = CooccurrenceRelationExtractor(auto_capitalized=True,
                                            window="paragraph")
        meta = _relations(ext, "TSMC. U.S. Army buys.")
        # 'TSMC' and 'U.S. Army' stay separate candidates instead of
        # fusing into one, even inside a single paragraph window; they
        # share that window, so exactly one clean pair is counted.
        self.assertEqual(meta["relations"],
                         [{"source": "TSMC", "target": "U.S. Army",
                           "count": 1}])

    def test_auto_capitalized_extra_stopwords(self):
        """Configured stopwords extend the built-in stoplist."""
        ext = CooccurrenceRelationExtractor(
            auto_capitalized=True, stopwords=["TSMC"])
        meta = _relations(ext, "TSMC met Samsung.")
        self.assertEqual(meta["relations"], [])

    def test_auto_capitalized_respects_abbreviation_guard(self):
        """'Inc.' stays inside the auto-detected name and window."""
        ext = CooccurrenceRelationExtractor(auto_capitalized=True)
        meta = _relations(ext, "Boeing Inc. supplies Airbus. Airbus agrees.")
        # The guarded period keeps 'Boeing Inc' and 'Airbus' in one
        # sentence; the second sentence holds Airbus alone (lowercase
        # 'agrees' breaks the sequence), so the pair counts once. The
        # trailing period of 'Inc.' is stripped from the candidate.
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing Inc",
                           "count": 1}])

    def test_auto_capitalized_with_alias_folding(self):
        """alias_map folds auto-detected surfaces onto canonicals."""
        ext = CooccurrenceRelationExtractor(
            auto_capitalized=True, alias_map={"Boeing Company": "Boeing"})
        meta = _relations(ext, "The Boeing Company met Airbus.")
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing", "count": 1}])

    def test_terms_plus_auto_capitalized_combined(self):
        """Configured terms and auto detection combine in one window."""
        ext = CooccurrenceRelationExtractor(
            terms=["Airbus"], auto_capitalized=True)
        meta = _relations(ext, "Boeing met Airbus.")
        self.assertEqual(meta["relations"],
                         [{"source": "Airbus", "target": "Boeing", "count": 1}])

    # ========== Metadata stamping ==========

    def test_metadata_stamping_preserves_and_copies(self):
        """Existing metadata survives; the original mapping is not mutated."""
        shared = {"lang": "en", "src": "reuters"}
        doc = Document(text=GROUND_TRUTH_TEXT, metadata=shared)
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Taiwan Semiconductor"])
        result = ext.process_docs([doc], self.query)

        self.assertIs(result[0], doc)
        self.assertEqual(doc.text, GROUND_TRUTH_TEXT)
        # The caller-held mapping is untouched: stamping worked on a copy.
        self.assertEqual(shared, {"lang": "en", "src": "reuters"})
        self.assertIsNot(doc.metadata, shared)
        self.assertEqual(doc.metadata["lang"], "en")
        self.assertEqual(doc.metadata["src"], "reuters")
        self.assertIn("relations", doc.metadata)
        self.assertIn("relation_graph", doc.metadata)

    def test_none_metadata_becomes_stamped_mapping(self):
        """Documents without metadata receive a fresh mapping."""
        doc = _doc("Apple met Samsung.")
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        ext.process_docs([doc], self.query)
        self.assertIsNotNone(doc.metadata)
        self.assertEqual(doc.metadata["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 1}])

    def test_documents_are_processed_independently(self):
        """Counts never leak from one document into the next."""
        ext = CooccurrenceRelationExtractor(terms=["Apple", "Samsung"])
        first = _doc("Apple met Samsung.")
        second = _doc("Only Apple here.")
        result = ext.process_docs([first, second], self.query)
        self.assertEqual(result[0].metadata["relations"],
                         [{"source": "Apple", "target": "Samsung", "count": 1}])
        self.assertEqual(result[1].metadata["relations"], [])

    def test_unconfigured_extractor_stamps_empty(self):
        """A directly constructed extractor without any tracking source
        warns and stamps empty relations rather than raising."""
        doc = _doc("Apple met Samsung.")
        result = self.extractor.process_docs([doc], self.query)
        self.assertEqual(result[0].metadata["relations"], [])
        self.assertEqual(result[0].metadata["relation_graph"], {})

    def test_determinism(self):
        """Repeated runs over identical input produce identical output."""
        ext = CooccurrenceRelationExtractor(
            terms=["Apple", "Samsung", "Taiwan Semiconductor"])
        first = _relations(ext, GROUND_TRUTH_TEXT)
        second = _relations(ext, GROUND_TRUTH_TEXT)
        self.assertEqual(first, second)
        self.assertEqual(list(first["relation_graph"].keys()),
                         sorted(first["relation_graph"].keys()))

    # ========== Configuration validation ==========

    def test_valid_full_configuration_loads(self):
        """Every parameter loads and validates from the configer."""
        configer = self._create_configer({
            "name": "cooccurrence_relation_extractor",
            "description": "test",
            "terms": ["Apple", "Samsung"],
            "alias_map": {"AAPL": "Apple"},
            "auto_capitalized": True,
            "window": "paragraph",
            "max_relations": 10,
            "min_count": 2,
            "stopwords": ["Airbus"],
        })
        ext = CooccurrenceRelationExtractor()
        ext.initialize_by_component_configer(configer)
        self.assertEqual(ext.terms, ["Apple", "Samsung"])
        self.assertEqual(ext.alias_map, {"AAPL": "Apple"})
        self.assertTrue(ext.auto_capitalized)
        self.assertEqual(ext.window, "paragraph")
        self.assertEqual(ext.max_relations, 10)
        self.assertEqual(ext.min_count, 2)
        self.assertEqual(ext.stopwords, ["Airbus"])

    def test_auto_capitalized_alone_is_valid(self):
        """auto_capitalized without terms is a legitimate configuration."""
        configer = self._create_configer({"auto_capitalized": True})
        ext = CooccurrenceRelationExtractor()
        ext.initialize_by_component_configer(configer)
        self.assertTrue(ext.auto_capitalized)
        self.assertEqual(ext.terms, [])

    def test_no_tracking_source_rejected(self):
        """Neither terms nor auto_capitalized fails at load time."""
        configer = self._create_configer({"window": "sentence"})
        ext = CooccurrenceRelationExtractor()
        with self.assertRaises(ValueError):
            ext.initialize_by_component_configer(configer)

    def test_invalid_terms_rejected(self):
        """terms must be a list of non-empty strings."""
        for bad in ["Apple", ["Apple", ""], ["Apple", 3]]:
            configer = self._create_configer(
                {"auto_capitalized": True, "terms": bad})
            ext = CooccurrenceRelationExtractor()
            with self.assertRaises(ValueError):
                ext.initialize_by_component_configer(configer)

    def test_invalid_alias_map_rejected(self):
        """alias_map must map non-empty strings to non-empty strings."""
        for bad in [{"AAPL": 3}, {"": "Apple"}, {"AAPL": ""}, ["AAPL"]]:
            configer = self._create_configer(
                {"auto_capitalized": True, "alias_map": bad})
            ext = CooccurrenceRelationExtractor()
            with self.assertRaises(ValueError):
                ext.initialize_by_component_configer(configer)

    def test_invalid_window_rejected(self):
        """window must be 'sentence' or 'paragraph'."""
        configer = self._create_configer(
            {"terms": ["Apple"], "window": "chapter"})
        ext = CooccurrenceRelationExtractor()
        with self.assertRaises(ValueError):
            ext.initialize_by_component_configer(configer)

    def test_invalid_max_relations_rejected(self):
        """max_relations must be an integer >= 1 (bools rejected)."""
        for bad in [0, -1, "many", 5.5, True]:
            configer = self._create_configer(
                {"terms": ["Apple"], "max_relations": bad})
            ext = CooccurrenceRelationExtractor()
            with self.assertRaises(ValueError):
                ext.initialize_by_component_configer(configer)

    def test_invalid_min_count_rejected(self):
        """min_count must be an integer >= 1 (bools rejected)."""
        for bad in [0, -2, "two", 1.5, False]:
            configer = self._create_configer(
                {"terms": ["Apple"], "min_count": bad})
            ext = CooccurrenceRelationExtractor()
            with self.assertRaises(ValueError):
                ext.initialize_by_component_configer(configer)

    def test_invalid_stopwords_rejected(self):
        """stopwords must be a list of non-empty strings."""
        for bad in ["Airbus", ["Airbus", ""], [1, 2]]:
            configer = self._create_configer(
                {"auto_capitalized": True, "stopwords": bad})
            ext = CooccurrenceRelationExtractor()
            with self.assertRaises(ValueError):
                ext.initialize_by_component_configer(configer)

    def test_duplicate_terms_deduplicated_in_order(self):
        """Exact duplicate terms collapse, keeping first-occurrence order."""
        configer = self._create_configer(
            {"terms": ["Apple", "Apple", "Samsung", "apple"]})
        ext = CooccurrenceRelationExtractor()
        ext.initialize_by_component_configer(configer)
        # 'apple' survives the exact-duplicate fold but maps onto the
        # same canonical as 'Apple' during matching.
        self.assertEqual(ext.terms, ["Apple", "Samsung", "apple"])
        surface_map = ext._build_surface_map()
        self.assertEqual(surface_map, {"apple": "Apple", "samsung": "Samsung"})

    # ========== Yaml definition ==========

    def test_shipped_yaml_definition_loads(self):
        """The shipped component yaml parses and initializes."""
        yaml_path = os.path.join(
            _REPO_ROOT, "agentuniverse", "agent", "action", "knowledge",
            "doc_processor", "cooccurrence_relation_extractor.yaml")
        self.assertTrue(os.path.isfile(yaml_path))
        with open(yaml_path, "r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle)
        cfg = Configer()
        cfg.value = value
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        ext = CooccurrenceRelationExtractor()
        ext.initialize_by_component_configer(configer)
        self.assertEqual(ext.terms,
                         ["Apple", "Samsung", "Taiwan Semiconductor"])
        self.assertEqual(ext.window, "sentence")
        self.assertEqual(ext.max_relations, 50)
        self.assertEqual(ext.min_count, 1)


if __name__ == "__main__":
    unittest.main()
