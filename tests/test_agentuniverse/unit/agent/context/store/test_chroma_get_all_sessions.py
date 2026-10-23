"""One row without `session_id` must not hide every session.

`get_all_sessions()` read `metadata["session_id"]` for every row inside a single
`try`, so a `KeyError` from one row aborted the loop and the handler returned
`[]`. The full list of sessions then looks empty while every segment is still
stored.

`get()` in the same class does the opposite and is the reference for the two
behaviour: it rebuilds each row inside its own `try`/`except ... continue`, so
one row it cannot reconstruct is skipped and the rest are returned.
"""

import types
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


class ConstantEmbedding:
    def __call__(self, input):
        return [[1.0, 0.0] for _ in input]


@pytest.fixture(autouse=True)
def isolated_chroma():
    SharedSystemClient.clear_system_cache()
    yield
    SharedSystemClient.clear_system_cache()


@pytest.fixture()
def store(tmp_path):
    instance = ChromaContextStore()
    instance.persist_directory = str(tmp_path / uuid.uuid4().hex)
    # chromadb keeps one process-global system per directory, so a fresh
    # directory (and a distinct collection name) per test keeps them apart.
    instance.collection_name = "sessions_" + uuid.uuid4().hex
    instance._setup_embedding_function = lambda: setattr(
        instance, "_embedding_function", ConstantEmbedding()
    )
    instance.initialize_by_component_configer(types.SimpleNamespace())
    return instance


def _segment(identifier):
    return ContextSegment(
        id=identifier,
        type=ContextType.CONVERSATION,
        priority=ContextPriority.HIGH,
        content=f"content for {identifier}",
        tokens=1,
    )


def test_lists_the_sessions_that_were_written(store):
    store.add([_segment("a1")], session_id="alpha")
    store.add([_segment("b1")], session_id="beta")

    assert sorted(store.get_all_sessions()) == ["alpha", "beta"]


def test_a_row_without_session_id_does_not_hide_the_others(store):
    """The regression: one foreign row used to make the result empty."""
    store.add([_segment("a1")], session_id="alpha")
    store.add([_segment("b1")], session_id="beta")

    store._collection.add(
        ids=["foreign"],
        documents=["written by something else"],
        embeddings=[[1.0, 0.0]],
        metadatas=[{"origin": "legacy"}],
    )

    assert sorted(store.get_all_sessions()) == ["alpha", "beta"]


def test_a_row_with_null_metadata_does_not_hide_the_others(store):
    store.add([_segment("a1")], session_id="alpha")

    store._collection.add(
        ids=["no-metadata"],
        documents=["row without metadata"],
        embeddings=[[1.0, 0.0]],
        metadatas=[None],
    )

    assert store.get_all_sessions() == ["alpha"]


def test_sessions_are_deduplicated(store):
    store.add([_segment("a1"), _segment("a2"), _segment("a3")], session_id="alpha")

    assert store.get_all_sessions() == ["alpha"]


def test_an_empty_collection_has_no_sessions(store):
    assert store.get_all_sessions() == []


def test_no_collection_yet_has_no_sessions():
    assert ChromaContextStore().get_all_sessions() == []


def test_get_still_returns_the_rows_it_can_rebuild(store):
    """The behaviour this method is being aligned with."""
    store.add([_segment("a1")], session_id="alpha")
    store._collection.add(
        ids=["foreign"],
        documents=["written by something else"],
        embeddings=[[1.0, 0.0]],
        metadatas=[{"session_id": "alpha"}],
    )

    assert [document.id for document in store.get(session_id="alpha")] == ["a1"]


def test_a_numeric_session_id_is_not_listed_because_get_cannot_read_it(store):
    """An id that `get()` cannot read back must not be advertised as a session.

    Chroma accepts ints as metadata values, but `get()` rebuilds a
    `ContextSegment` whose `session_id` is `Optional[str]`, so a row carrying a
    numeric session_id raises there and yields no segments. Listing the int made
    callers see a session they could never read; the row is skipped instead.
    """
    store.add([_segment("a1")], session_id="alpha")
    row_id = store._collection.get()["ids"][0]
    metadata = dict(store._collection.get(include=["metadatas"])["metadatas"][0])
    metadata["session_id"] = 999
    store._collection.update(ids=[row_id], metadatas=[metadata])

    sessions = store.get_all_sessions()

    assert 999 not in sessions
    assert all(isinstance(session, str) for session in sessions)
    assert store.get(session_id=999) == []


def test_every_listed_session_can_actually_be_read(store):
    """The invariant the previous test protects: listed implies readable."""
    store.add([_segment("a1")], session_id="alpha")
    store.add([_segment("b1")], session_id="beta")
    store._collection.add(
        ids=["foreign-numeric"],
        documents=["written by something else"],
        embeddings=[[0.9, 0.1]],
        metadatas=[{"session_id": 42}],
    )

    sessions = store.get_all_sessions()

    assert sorted(sessions) == ["alpha", "beta"]
    for session in sessions:
        assert store.get(session_id=session), f"{session} was listed but is empty"
