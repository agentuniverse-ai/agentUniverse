#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for ReciprocalRankFusionProcessor.

Covers single-channel fallback, multi-channel RRF fusion, cross-channel
de-duplication, the RRF score formula, top_n bounding, channel detection,
in-place metadata scoring, and config loading.
"""

import unittest
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.doc_processor.\
    reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.store.document import Document


def _doc(text: str, channel: str = None) -> Document:
    """Build a Document, optionally tagging it with a retrieval channel."""
    metadata = {"channel": channel} if channel else None
    return Document(text=text, metadata=metadata)


class TestSingleChannel(unittest.TestCase):
    """Single-channel mode (no channel_key): position-based scoring."""

    def test_empty_input_returns_empty(self) -> None:
        """No documents → no output documents."""
        proc = ReciprocalRankFusionProcessor()
        self.assertEqual(proc._process_docs([]), [])

    def test_default_is_single_channel_and_preserves_order(self) -> None:
        """With no channel_key the input order is preserved."""
        proc = ReciprocalRankFusionProcessor()
        docs = [_doc("alpha"), _doc("beta"), _doc("gamma")]
        out = proc._process_docs(docs)
        self.assertEqual([d.text for d in out], ["alpha", "beta", "gamma"])

    def test_single_channel_scores_decrease_with_rank(self) -> None:
        """Earlier positions get strictly higher fused scores (k=60)."""
        proc = ReciprocalRankFusionProcessor(k=60)
        docs = [_doc("alpha"), _doc("beta"), _doc("gamma")]
        out = proc._process_docs(docs)
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 1.0 / 61)
        self.assertAlmostEqual(out[1].metadata["relevance_score"], 1.0 / 62)
        self.assertAlmostEqual(out[2].metadata["relevance_score"], 1.0 / 63)

    def test_metadata_other_keys_preserved(self) -> None:
        """Pre-existing metadata survives the score being written."""
        proc = ReciprocalRankFusionProcessor()
        doc = Document(text="alpha", metadata={"source": "wiki", "lang": "en"})
        out = proc._process_docs([doc])
        self.assertEqual(out[0].metadata["source"], "wiki")
        self.assertEqual(out[0].metadata["lang"], "en")
        self.assertIn("relevance_score", out[0].metadata)


class TestMultiChannelFusion(unittest.TestCase):
    """Multi-channel mode: documents grouped by channel metadata."""

    def test_doc_in_two_channels_outranks_single_channel_top(self) -> None:
        """A doc ranking low in two channels beats one ranking #1 in one."""
        proc = ReciprocalRankFusionProcessor(channel_key="channel", k=60)
        docs = [
            _doc("shared", "vector"), _doc("only_vector", "vector"),
            _doc("shared", "keyword"), _doc("only_keyword", "keyword"),
        ]
        out = proc._process_docs(docs)
        # 'shared' ranks #1 (rank 0) in both channels: 2 * (1/61).
        # 'only_vector'/'only_keyword' rank #2 (rank 1) in their single channel.
        self.assertEqual(out[0].text, "shared")
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 2.0 / 61)
        # The single-channel docs tie at 1/62 (rank 1, k=60).
        self.assertAlmostEqual(out[1].metadata["relevance_score"], 1.0 / 62)

    def test_score_formula_rank_one_plus_k(self) -> None:
        """Contribution of a rank-r position is exactly 1/(k + r + 1)."""
        proc = ReciprocalRankFusionProcessor(channel_key="channel", k=10)
        docs = [
            _doc("first", "vector"),
            _doc("second", "vector"),
            _doc("first", "keyword"),  # rank 0 again
        ]
        out = proc._process_docs(docs)
        score_by_text = {d.text: d.metadata["relevance_score"] for d in out}
        self.assertAlmostEqual(score_by_text["first"], 2.0 / 11)
        self.assertAlmostEqual(score_by_text["second"], 1.0 / 12)

    def test_cross_channel_dedup_by_id(self) -> None:
        """Same doc (same id) in two channels is returned once, scores merged."""
        proc = ReciprocalRankFusionProcessor(channel_key="channel")
        # Two distinct Documents with identical text → same deterministic id.
        d1 = Document(text="dup", metadata={"channel": "vector"})
        d2 = Document(text="dup", metadata={"channel": "keyword"})
        out = proc._process_docs([d1, d2])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "dup")
        # Merged across both rank-0 positions.
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 2.0 / 61)

    def test_dedup_within_a_channel(self) -> None:
        """A doc repeated inside one channel is only counted once there."""
        proc = ReciprocalRankFusionProcessor(channel_key="channel")
        docs = [
            _doc("repeat", "vector"),
            _doc("repeat", "vector"),  # same id → ignored within channel
            _doc("other", "vector"),
        ]
        out = proc._process_docs(docs)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0].text, "repeat")
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 1.0 / 61)

    def test_dedup_by_text(self) -> None:
        """dedup_key='text' collapses documents with equal content."""
        proc = ReciprocalRankFusionProcessor(
            channel_key="channel", dedup_key="text")
        docs = [
            _doc("same text", "vector"),
            _doc("same text", "keyword"),
        ]
        out = proc._process_docs(docs)
        self.assertEqual(len(out), 1)

    def test_dedup_by_custom_metadata_field(self) -> None:
        """dedup_key pointing at a metadata field collapses matching docs."""
        proc = ReciprocalRankFusionProcessor(
            channel_key="channel", dedup_key="source")
        docs = [
            Document(text="a", metadata={"channel": "vector", "source": "db"}),
            Document(text="b", metadata={"channel": "keyword", "source": "db"}),
        ]
        out = proc._process_docs(docs)
        # Same 'source' value across two channels → fused into one result.
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 2.0 / 61)

    def test_custom_dedup_key_missing_does_not_collapse(self) -> None:
        """Documents lacking the configured dedup field fall back to their id.

        Without the fallback every such document would share a None identity
        and be collapsed into a single result.
        """
        proc = ReciprocalRankFusionProcessor(
            channel_key="channel", dedup_key="source")
        docs = [
            Document(text="alpha", metadata={"channel": "vector"}),
            Document(text="beta", metadata={"channel": "keyword"}),
            Document(text="gamma", metadata={"channel": "vector"}),
        ]
        out = proc._process_docs(docs)
        # None of the docs carry 'source'; each keeps its unique id, so all
        # three survive (no spurious collapse).
        self.assertEqual(len(out), 3)
        self.assertEqual(
            {d.text for d in out}, {"alpha", "beta", "gamma"})

    def test_custom_dedup_key_mixed_presence(self) -> None:
        """A doc carrying the field still dedups; one without it does not."""
        proc = ReciprocalRankFusionProcessor(
            channel_key="channel", dedup_key="source")
        docs = [
            Document(text="shared", metadata={"channel": "vector", "source": "db"}),
            Document(text="shared", metadata={"channel": "keyword", "source": "db"}),
            Document(text="lonely", metadata={"channel": "vector"}),
        ]
        out = proc._process_docs(docs)
        # The two 'shared' docs fuse (same source); 'lonely' has no source and
        # falls back to its own id, so it stays separate.
        self.assertEqual(len(out), 2)

    def test_channel_key_absent_falls_back_to_single_channel(self) -> None:
        """If no document carries the channel field, one channel is assumed."""
        proc = ReciprocalRankFusionProcessor(channel_key="channel")
        docs = [_doc("a"), _doc("b"), _doc("c")]  # no channel metadata
        out = proc._process_docs(docs)
        # Single channel → order preserved, scores are positional.
        self.assertEqual([d.text for d in out], ["a", "b", "c"])
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 1.0 / 61)


class TestTopNAndScoreField(unittest.TestCase):
    """top_n bounding and custom score_field."""

    def test_top_n_truncates(self) -> None:
        """Only the top_n highest-scoring documents are returned."""
        proc = ReciprocalRankFusionProcessor(top_n=2)
        docs = [_doc("a"), _doc("b"), _doc("c"), _doc("d")]
        out = proc._process_docs(docs)
        self.assertEqual(len(out), 2)
        self.assertEqual([d.text for d in out], ["a", "b"])

    def test_top_n_zero_returns_empty(self) -> None:
        proc = ReciprocalRankFusionProcessor(top_n=0)
        out = proc._process_docs([_doc("a"), _doc("b")])
        self.assertEqual(out, [])

    def test_custom_score_field(self) -> None:
        """The fused score is written under the configured metadata key."""
        proc = ReciprocalRankFusionProcessor(score_field="rrf_score")
        out = proc._process_docs([_doc("a")])
        self.assertIn("rrf_score", out[0].metadata)
        self.assertNotIn("relevance_score", out[0].metadata)


class TestConfigLoading(unittest.TestCase):
    """Tests for _initialize_by_component_configer."""

    def test_config_fields_loaded(self) -> None:
        """Configer attributes are mapped onto the processor fields."""
        proc = ReciprocalRankFusionProcessor()
        configer = SimpleNamespace(
            name="my_fuser",
            description="desc",
            channel_key="source",
            dedup_key="text",
            k=40,
            top_n=5,
            score_field="fused",
        )
        proc._initialize_by_component_configer(configer)
        self.assertEqual(proc.name, "my_fuser")
        self.assertEqual(proc.channel_key, "source")
        self.assertEqual(proc.dedup_key, "text")
        self.assertEqual(proc.k, 40)
        self.assertEqual(proc.top_n, 5)
        self.assertEqual(proc.score_field, "fused")

    def test_config_defaults_when_absent(self) -> None:
        """Missing optional attributes leave the defaults intact."""
        proc = ReciprocalRankFusionProcessor()
        configer = SimpleNamespace(name="n", description="d")
        proc._initialize_by_component_configer(configer)
        self.assertIsNone(proc.channel_key)
        self.assertEqual(proc.dedup_key, "id")
        self.assertEqual(proc.k, 60)
        self.assertIsNone(proc.top_n)
        self.assertEqual(proc.score_field, "relevance_score")


if __name__ == '__main__':
    unittest.main()
