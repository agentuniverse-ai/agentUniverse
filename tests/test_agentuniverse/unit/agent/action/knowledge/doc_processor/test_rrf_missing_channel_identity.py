"""A missing recall channel must not alias a user-provided channel name."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize("missing", [None, {}, {"channel": None}])
@pytest.mark.parametrize("reverse", [False, True])
def test_missing_and_literal_default_channels_contribute_separately(missing, reverse):
    """Both channels vote even when their representative document is identical."""
    docs = [Document(text="shared", metadata=missing),
            Document(text="shared", metadata={"channel": "__default__"})]
    if reverse:
        docs.reverse()
    original_metadata = dict(docs[0].metadata or {})
    result = ReciprocalRankFusionProcessor(channel_key="channel").process_docs(docs)
    assert len(result) == 1
    assert result[0] is docs[0]
    assert result[0].metadata["relevance_score"] == pytest.approx(2 / 61)
    assert {key: value for key, value in result[0].metadata.items()
            if key != "relevance_score"} == original_metadata


def test_all_missing_variants_share_one_ranked_channel():
    """Absent metadata, absent key and explicit None retain the old fallback."""
    docs = [Document(text="a", metadata=None), Document(text="b", metadata={}),
            Document(text="c", metadata={"channel": None})]
    result = ReciprocalRankFusionProcessor(channel_key="channel").process_docs(docs)
    assert [doc.text for doc in result] == ["a", "b", "c"]
    assert [doc.metadata["relevance_score"] for doc in result] == pytest.approx(
        [1 / 61, 1 / 62, 1 / 63])


def test_interleaved_channels_keep_their_own_ranks_and_first_seen_order():
    """Grouping must not mix positions or reorder documents within a channel."""
    docs = [Document(text="a"),
            Document(text="b", metadata={"channel": "__default__"}),
            Document(text="c", metadata={"channel": None}),
            Document(text="d", metadata={"channel": "__default__"})]
    processor = ReciprocalRankFusionProcessor(channel_key="channel")
    groups = processor._group_channels(docs)
    assert groups == [[docs[0], docs[2]], [docs[1], docs[3]]]
    scores = {doc.text: doc.metadata["relevance_score"]
              for doc in processor.process_docs(docs)}
    assert scores == pytest.approx({"a": 1 / 61, "b": 1 / 61,
                                   "c": 1 / 62, "d": 1 / 62})


@pytest.mark.parametrize("dedup_key", ["text", "source"])
def test_custom_deduplication_and_score_field(dedup_key):
    """The fix applies before deduplication and does not alter output policy."""
    docs = [Document(id="first", text="shared", metadata={"source": "s"}),
            Document(id="second", text="shared",
                     metadata={"source": "s", "custom_channel": "__default__"})]
    result = ReciprocalRankFusionProcessor(
        channel_key="custom_channel", dedup_key=dedup_key,
        score_field="fused", k=0, top_n=1).process_docs(docs)
    assert result == [docs[0]]
    assert result[0].metadata == {"source": "s", "fused": 2.0}
    assert docs[1].metadata == {"source": "s", "custom_channel": "__default__"}


def test_duplicates_within_each_channel_are_counted_once():
    """A duplicate does not create an extra vote in either bucket."""
    docs = [Document(text="shared"), Document(text="shared"),
            Document(text="shared", metadata={"channel": "__default__"}),
            Document(text="shared", metadata={"channel": "__default__"})]
    result = ReciprocalRankFusionProcessor(channel_key="channel").process_docs(docs)
    assert len(result) == 1
    assert result[0].metadata["relevance_score"] == pytest.approx(2 / 61)


@pytest.mark.parametrize("channel_key", [None, ""])
def test_disabled_channel_detection_remains_single_channel(channel_key):
    """No configured channel field means one vote regardless of metadata."""
    docs = [Document(text="shared"),
            Document(text="shared", metadata={"channel": "__default__"})]
    result = ReciprocalRankFusionProcessor(channel_key=channel_key).process_docs(docs)
    assert result[0].metadata["relevance_score"] == pytest.approx(1 / 61)


def test_repeated_calls_do_not_share_missing_bucket_contents():
    """A sentinel must not retain documents between queries."""
    processor = ReciprocalRankFusionProcessor(channel_key="channel")
    processor.process_docs([Document(text="first")])
    result = processor.process_docs([Document(text="second")])
    assert [doc.text for doc in result] == ["second"]
    assert result[0].metadata["relevance_score"] == pytest.approx(1 / 61)
