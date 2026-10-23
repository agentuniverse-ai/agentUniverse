"""Cold-tier semantic search must return something.

`search()` converted Chroma's distance with `similarity = 1.0 - distance` and
compared it against `similarity_threshold` (default `0.7`). That formula only
makes sense for a distance already normalised to `[0, 1]`, but the collection
was created without `hnsw:space`, so Chroma defaulted to **L2 squared**, whose
range is unbounded above. Every realistic distance therefore produced a
similarity at or below zero and was filtered out:

    distance=2.0 -> similarity=-1.0   below 0.7, dropped
    distance=4.0 -> similarity=-3.0   below 0.7, dropped

`RamContextStore.search()` on the same data returns the matching segments, so
the two backends disagreed about whether anything matched.

The negative score also violated `ContextMetadata.relevance_score`, declared as
`Field(default=1.0, ge=0.0, le=1.0)`; the assignment went through because
pydantic does not validate on attribute assignment.
"""

import uuid

import pytest

chromadb = pytest.importorskip("chromadb")
from chromadb.api.client import SharedSystemClient  # noqa: E402

from agentuniverse.agent.context.context_model import (  # noqa: E402
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.chroma_context_store import (  # noqa: E402
    ChromaContextStore,
)

VOCAB = ["python", "machine", "learning", "cooking", "pasta", "recipe", "web", "framework"]


def _embed(text):
    lowered = text.lower()
    vector = [1.0 if word in lowered else 0.0 for word in VOCAB]
    return vector if any(vector) else [0.0001] * len(VOCAB)


class VocabularyEmbedding:
    """Distinguishes texts by the words they contain, so search is meaningful."""

    def __call__(self, input):
        return [_embed(text) for text in input]


@pytest.fixture(autouse=True)
def isolated_chroma():
    SharedSystemClient.clear_system_cache()
    yield
    SharedSystemClient.clear_system_cache()


@pytest.fixture()
def store(tmp_path):
    instance = ChromaContextStore()
    instance.persist_directory = str(tmp_path / uuid.uuid4().hex)
    instance.collection_name = "semantic_" + uuid.uuid4().hex
    instance._setup_embedding_function = lambda: setattr(
        instance, "_embedding_function", VocabularyEmbedding()
    )
    instance.initialize_by_component_configer(__import__("types").SimpleNamespace())
    instance.add(
        [
            ContextSegment(
                id="s1",
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="python machine learning",
                tokens=1,
            ),
            ContextSegment(
                id="s2",
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="cooking pasta recipe",
                tokens=1,
            ),
            ContextSegment(
                id="s3",
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="python web framework",
                tokens=1,
            ),
        ],
        session_id="session",
    )
    return instance


def test_the_collection_is_created_with_cosine_space(store):
    """The conversion below only holds for this metric."""
    assert (store._collection.metadata or {}).get("hnsw:space") == "cosine"


def test_search_returns_the_matching_segments(store):
    hits = store.search(session_id="session", query="python")

    assert sorted(segment.id for segment in hits) == ["s1", "s3"]


def test_search_returns_only_the_closest_segment_for_a_narrow_query(store):
    hits = store.search(session_id="session", query="cooking")

    assert [segment.id for segment in hits] == ["s2"]


def test_search_excludes_the_unrelated_segment(store):
    """The control: `cooking pasta recipe` must not come back for 'python'."""
    hits = store.search(session_id="session", query="python")

    assert "s2" not in {segment.id for segment in hits}


def test_relevance_score_stays_inside_its_declared_range(store):
    """`relevance_score` is declared `ge=0.0, le=1.0`."""
    for segment in store.search(session_id="session", query="python"):
        assert 0.0 <= segment.metadata.relevance_score <= 1.0


def test_a_matching_segment_scores_higher_than_an_unrelated_one(store):
    """Ordering, without depending on the absolute threshold."""
    hits = store.search(session_id="session", query="python", min_similarity=0.0)
    scores = {segment.id: segment.metadata.relevance_score for segment in hits}

    assert scores["s1"] > scores["s2"]
    assert scores["s3"] > scores["s2"]


def test_distance_conversion_is_bounded_for_every_space(store):
    """The helper must never produce a value outside [0, 1]."""
    for distance in (0.0, 0.3, 1.0, 2.0, 4.0, 100.0):
        similarity = store._distance_to_similarity(distance)
        assert 0.0 <= similarity <= 1.0, (distance, similarity)

    assert store._distance_to_similarity(0.0) == 1.0


def test_distance_conversion_handles_an_l2_collection(store):
    """Legacy collections were created with the default L2 space."""
    store._collection.metadata = {"description": "legacy", "hnsw:space": "l2"}

    # 1 / (1 + d): bounded and monotone, unlike `1 - d`.
    assert store._distance_to_similarity(0.0) == pytest.approx(1.0)
    assert store._distance_to_similarity(1.0) == pytest.approx(0.5)
    assert store._distance_to_similarity(3.0) == pytest.approx(0.25)


def test_clear_all_keeps_the_metric(store):
    """Recreating the collection must not fall back to L2.

    `clear_all()` deletes and recreates the collection. If the recreate drops
    `hnsw:space`, the physical index becomes L2 while `search()` still rescales
    as if it were cosine, and the same data stops matching:

        before clear_all: space=cosine  similarity(0.4233)=0.7883 -> 1 hit
        after  clear_all: space=None    similarity(0.4233)=0.7026 -> 0 hits
    """
    assert (store._collection.metadata or {}).get("hnsw:space") == "cosine"

    store.clear_all()

    assert (store._collection.metadata or {}).get("hnsw:space") == "cosine"


def test_search_still_works_after_clear_all(store):
    """The user-visible consequence of the metric being preserved.

    The fixture already holds three segments; this only needs to check that the
    same query keeps matching after the collection is recreated.
    """
    before = sorted(segment.id for segment in store.search(session_id="session", query="python"))
    assert before == ["s1", "s3"]

    store.clear_all()

    assert store.search(session_id="session", query="python") == []

    store.add(
        [
            ContextSegment(
                id="renamed-1",
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="python machine learning",
                tokens=1,
            )
        ],
        session_id="session",
    )

    assert [
        segment.id for segment in store.search(session_id="session", query="python")
    ] == ["renamed-1"]
