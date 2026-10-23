"""`clear_all()` must not report success when the data is still there.

It used to wrap the whole delete-and-recreate in `except Exception: pass`, so
any failure -- a locked database, a permissions error, a provider error -- left
every archived segment in place and returned normally. The caller could not
tell the difference between "cleared" and "still holding the data", which
matters for a method whose only purpose is removal.

`RamContextStore.clear_all()` and `RedisContextStore.clear_all()` let their
errors propagate; Chroma was the only store that swallowed them.
"""

import types

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
    """A persistent store with one archived segment in it."""
    instance = ChromaContextStore()
    instance.persist_directory = str(tmp_path / "cold")
    instance.collection_name = "clear_all_probe"
    instance._setup_embedding_function = lambda: setattr(
        instance, "_embedding_function", ConstantEmbedding()
    )
    instance.initialize_by_component_configer(types.SimpleNamespace())
    instance.add(
        [
            ContextSegment(
                id="segment-1",
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="archived context",
                tokens=2,
            )
        ],
        session_id="session-1",
    )
    return instance


class _Named:
    def __init__(self, name):
        self.name = name


class FailingClient:
    """A client whose collection operations fail, like a locked database.

    `list_collections()` reports the collection as present, so `clear_all()`
    takes the delete path and the failure surfaces -- which is the situation
    these tests are about.
    """

    def __init__(self, message="database is locked", present=True):
        self.message = message
        self.present = present

    def list_collections(self):
        return [_Named("clear_all_probe")] if self.present else []

    def delete_collection(self, name):
        raise RuntimeError(self.message)

    def create_collection(self, **kwargs):
        raise RuntimeError(self.message)


class AbsentClient:
    """A client whose collection is already gone: deleting it must not error."""

    def __init__(self):
        self.delete_called = False

    def list_collections(self):
        return []

    def delete_collection(self, name):
        self.delete_called = True
        raise AssertionError("delete_collection must not be called when absent")

    def create_collection(self, **kwargs):
        return kwargs


def test_clear_all_propagates_a_delete_failure(store):
    store._chroma_client = FailingClient()

    with pytest.raises(RuntimeError, match="database is locked"):
        store.clear_all()


def test_clear_all_reports_the_failure_instead_of_looking_successful(store):
    """The old behaviour: returns normally, data still readable."""
    store._chroma_client = FailingClient()

    try:
        store.clear_all()
    except RuntimeError:
        return
    pytest.fail(
        "clear_all() returned successfully although the collection was never deleted"
    )


def test_clear_all_removes_the_segments_on_the_happy_path(store):
    assert store.get(session_id="session-1")

    store.clear_all()

    assert store.get(session_id="session-1") == []


def test_clear_all_is_idempotent(store):
    store.clear_all()
    store.clear_all()

    assert store.get(session_id="session-1") == []


def test_clear_all_tolerates_a_collection_that_is_already_gone(store):
    """Deleting an absent collection is not an error: the data is clear."""
    store._chroma_client.delete_collection(name=store.collection_name)

    store.clear_all()

    assert store.get(session_id="session-1") == []


def test_clear_all_does_nothing_without_a_collection():
    instance = ChromaContextStore()

    instance.clear_all()  # must not raise

    assert instance._collection is None


def test_clear_all_does_not_delete_an_absent_collection(store):
    """Presence is checked first, so no exception has to be interpreted."""
    client = AbsentClient()
    store._chroma_client = client

    store.clear_all()

    assert client.delete_called is False


def test_clear_all_is_not_fooled_by_an_unrelated_value_error(store):
    """The old string check swallowed any message containing "does not exist".

    chromadb 0.4.24 raises a bare `ValueError("Collection X does not exist.")`
    for a missing collection, so the previous implementation matched on the text
    and would also have accepted, for example,
    `ValueError("... path does not exist ...")`.
    """
    store._chroma_client = FailingClient(
        message="cannot delete: the backing path does not exist"
    )

    with pytest.raises(RuntimeError, match="backing path does not exist"):
        store.clear_all()
