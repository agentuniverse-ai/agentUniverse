# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : Yue Wang
# @FileName: test_lost_in_the_middle_reorderer.py

import unittest

from agentuniverse.agent.action.knowledge.doc_processor.\
    lost_in_the_middle_reorderer import LostInTheMiddleReorderer
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


def _doc(text: str, score=None, score_field: str = "relevance_score"):
    """Build a Document with an optional relevance score in its metadata."""
    metadata = {} if score is None else {score_field: score}
    return Document(text=text, metadata=metadata)


class TestLostInTheMiddleReorderer(unittest.TestCase):
    """Offline unit tests for the LostInTheMiddleReorderer processor."""

    def setUp(self):
        self.processor = LostInTheMiddleReorderer()

    # ------------------------------------------------------------------ #
    # Trivial inputs
    # ------------------------------------------------------------------ #

    def test_empty_input_returns_empty(self):
        self.assertEqual(self.processor.process_docs([]), [])

    def test_single_document_passthrough(self):
        docs = [_doc("only", 0.9)]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result], ["only"])

    def test_two_documents_passthrough(self):
        """With two documents both positions are already strong positions."""
        docs = [_doc("weak", 0.1), _doc("strong", 0.9)]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result], ["weak", "strong"])

    # ------------------------------------------------------------------ #
    # Missing score handling
    # ------------------------------------------------------------------ #

    def test_no_scores_returns_input_unchanged(self):
        docs = [_doc(f"doc{i}") for i in range(5)]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result],
                         [f"doc{i}" for i in range(5)])

    def test_non_numeric_score_treated_as_missing(self):
        docs = [
            _doc("a", "high"),
            _doc("b", 0.5),
            _doc("c", "0.9"),
        ]
        # Only "b" carries a numeric score: no re-order signal collapse, the
        # other docs are unscored and must survive.
        result = self.processor.process_docs(docs)
        self.assertEqual(len(result), 3)
        self.assertEqual({d.text for d in result}, {"a", "b", "c"})

    def test_boolean_score_treated_as_missing(self):
        docs = [_doc("a", True), _doc("b", False), _doc("c", True)]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result], ["a", "b", "c"])

    def test_nan_and_infinite_scores_treated_as_missing(self):
        docs = [_doc("a", float("nan")), _doc("b", float("inf")), _doc("c")]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result], ["a", "b", "c"])

    # ------------------------------------------------------------------ #
    # Core lost-in-the-middle layout
    # ------------------------------------------------------------------ #

    def test_classic_four_document_layout(self):
        """Ranked 0.9, 0.6, 0.4, 0.1 must land as 0.9, 0.4, 0.1, 0.6."""
        docs = [_doc("d1", 0.1), _doc("d2", 0.4), _doc("d3", 0.9),
                _doc("d4", 0.6)]
        result = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in result],
                         ["d3", "d2", "d1", "d4"])

    def test_best_first_second_best_last(self):
        docs = [_doc(f"d{i}", i) for i in range(1, 6)]  # scores 1..5
        result = self.processor.process_docs(docs)
        self.assertEqual(result[0].text, "d5")   # best at the front
        self.assertEqual(result[-1].text, "d4")  # runner-up at the end
        self.assertEqual(result[1].text, "d3")   # third at the front+1
        self.assertEqual(result[-2].text, "d2")  # fourth at the end-1
        self.assertEqual(result[2].text, "d1")   # weakest in the middle

    def test_weakest_documents_in_middle_for_odd_list(self):
        scores = [10, 20, 30, 40, 50, 60, 70]
        docs = [_doc(f"d{s}", s) for s in scores]
        result = self.processor.process_docs(docs)
        texts = [d.text for d in result]
        # Ends carry the two strongest docs.
        self.assertEqual(set(texts[0:1] + texts[-1:]), {"d70", "d60"})
        # The exact middle slot holds the weakest document.
        self.assertEqual(texts[3], "d10")
        # The middle three slots hold the three weakest documents.
        self.assertEqual(set(texts[2:5]), {"d10", "d20", "d30"})

    def test_all_documents_preserved(self):
        docs = [_doc(f"d{i}", i) for i in range(10)]
        result = self.processor.process_docs(docs)
        self.assertEqual(len(result), 10)
        self.assertEqual({d.id for d in result}, {d.id for d in docs})

    def test_metadata_not_mutated(self):
        docs = [_doc("a", 0.1), _doc("b", 0.9), _doc("c", 0.5)]
        before = {d.id: dict(d.metadata) for d in docs}
        self.processor.process_docs(docs)
        for d in docs:
            self.assertEqual(d.metadata, before[d.id])

    # ------------------------------------------------------------------ #
    # Ties and mixed scored/unscored inputs
    # ------------------------------------------------------------------ #

    def test_equal_scores_keep_input_order(self):
        docs = [_doc("a", 0.5), _doc("b", 0.5), _doc("c", 0.5),
                _doc("d", 0.5)]
        result = self.processor.process_docs(docs)
        # Dealt alternately front/back from a stable ranking: a, c, d, b.
        self.assertEqual([d.text for d in result], ["a", "c", "d", "b"])

    def test_unscored_docs_follow_scored_in_input_order(self):
        docs = [
            _doc("scored_low", 0.1),
            _doc("unscored_1"),
            _doc("scored_high", 0.9),
            _doc("unscored_2"),
            _doc("scored_mid", 0.5),
        ]
        result = self.processor.process_docs(docs)
        texts = [d.text for d in result]
        # Ranking: scored_high, scored_mid, scored_low, unscored_1, unscored_2.
        # Dealt by position strength (0 > 4 > 1 > 3 > 2): the best doc takes
        # the first slot, the runner-up the last slot, then scored_low,
        # unscored_1, unscored_2 fill progressively weaker middle slots.
        self.assertEqual(texts,
                         ["scored_high", "scored_low", "unscored_2",
                          "unscored_1", "scored_mid"])

    def test_unscored_docs_never_dropped(self):
        docs = [_doc("u1"), _doc("s1", 0.9), _doc("u2"), _doc("s2", 0.1),
                _doc("u3"), _doc("s3", 0.5), _doc("u4")]
        result = self.processor.process_docs(docs)
        self.assertEqual(len(result), 7)
        self.assertEqual({d.text for d in result},
                         {"u1", "u2", "u3", "u4", "s1", "s2", "s3"})

    # ------------------------------------------------------------------ #
    # Query / determinism / configuration
    # ------------------------------------------------------------------ #

    def test_query_argument_accepted_and_ignored(self):
        docs = [_doc("a", 0.1), _doc("b", 0.9), _doc("c", 0.5)]
        query = Query(query_str="anything", similarity_top_k=3)
        with_query = self.processor.process_docs(docs, query=query)
        without_query = self.processor.process_docs(docs)
        self.assertEqual([d.text for d in with_query],
                         [d.text for d in without_query])

    def test_repeated_runs_are_deterministic(self):
        import random
        random.seed(248)
        scores = [random.random() for _ in range(20)]
        docs = [_doc(f"d{i}", s) for i, s in enumerate(scores)]
        first = [d.id for d in self.processor.process_docs(list(docs))]
        second = [d.id for d in self.processor.process_docs(list(docs))]
        third = [d.id for d in self.processor.process_docs(list(docs))]
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_custom_score_field(self):
        processor = LostInTheMiddleReorderer(score_field="fusion_score")
        docs = [
            Document(text="a", metadata={"relevance_score": 0.9,
                                         "fusion_score": 0.1}),
            Document(text="b", metadata={"relevance_score": 0.1,
                                         "fusion_score": 0.9}),
            Document(text="c", metadata={"relevance_score": 0.5,
                                         "fusion_score": 0.5}),
        ]
        result = processor.process_docs(docs)
        # Ranked by fusion_score: b, c, a -> dealt b, a, c.
        self.assertEqual([d.text for d in result], ["b", "a", "c"])

    def test_initialize_by_component_configer(self):
        configer = ComponentConfiger()
        configer.name = 'lost_in_the_middle_reorderer'
        configer.description = 'test'
        configer.score_field = 'rrf_score'
        processor = LostInTheMiddleReorderer()
        processor._initialize_by_component_configer(configer)
        self.assertEqual(processor.score_field, 'rrf_score')
        self.assertEqual(processor.name, 'lost_in_the_middle_reorderer')

    def test_initialize_without_score_field_keeps_default(self):
        configer = ComponentConfiger()
        configer.name = 'lost_in_the_middle_reorderer'
        configer.description = 'test'
        processor = LostInTheMiddleReorderer()
        processor._initialize_by_component_configer(configer)
        self.assertEqual(processor.score_field, 'relevance_score')

    def test_initialize_rejects_empty_score_field(self):
        configer = ComponentConfiger()
        configer.name = 'lost_in_the_middle_reorderer'
        configer.description = 'test'
        configer.score_field = ''
        with self.assertRaises(ValueError):
            LostInTheMiddleReorderer()._initialize_by_component_configer(
                configer)

    def test_initialize_rejects_non_string_score_field(self):
        configer = ComponentConfiger()
        configer.name = 'lost_in_the_middle_reorderer'
        configer.description = 'test'
        configer.score_field = 123
        with self.assertRaises(ValueError):
            LostInTheMiddleReorderer()._initialize_by_component_configer(
                configer)

    # ------------------------------------------------------------------ #
    # Deal-onto-positions helper
    # ------------------------------------------------------------------ #

    def test_deal_onto_positions_pattern(self):
        ranked = [_doc(f"r{i}") for i in range(6)]
        result = LostInTheMiddleReorderer._deal_onto_positions(ranked)
        self.assertEqual([d.text for d in result],
                         ["r0", "r2", "r4", "r5", "r3", "r1"])


if __name__ == '__main__':
    unittest.main()
