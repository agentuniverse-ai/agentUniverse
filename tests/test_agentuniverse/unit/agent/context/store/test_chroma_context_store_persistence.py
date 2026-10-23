"""ChromaContextStore must actually write to the directory it is given.

`ChromaContextStore` is the cold storage tier: its docstring promises
"long-term context archival (>72 hours)" and it takes a `persist_directory`.
It built its client from `Settings(persist_directory=..., anonymized_telemetry
=False)`, which leaves `is_persistent` at its default `False`, so chromadb
handed back an in-memory EphemeralClient. The directory stayed empty and every
archived segment disappeared with the process.

Both tests below observe the store from the outside: one checks that the data
lands on disk, the other that two stores configured with different directories
can exist in the same process (chromadb keys its global system on
"ephemeral" for every non-persistent client, so two of them collided).
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
    """Deterministic two-dimensional embedding, so no model is downloaded."""

    def __call__(self, input):
        return [[1.0, 0.0] for _ in input]


@pytest.fixture(autouse=True)
def isolated_chroma():
    """Do not inherit (or leave behind) another test's global Chroma system."""
    SharedSystemClient.clear_system_cache()
    yield
    SharedSystemClient.clear_system_cache()


def _build_store(persist_directory, collection_name="context_probe"):
    store = ChromaContextStore()
    store.persist_directory = str(persist_directory)
    store.collection_name = collection_name
    store._setup_embedding_function = lambda: setattr(
        store, "_embedding_function", ConstantEmbedding()
    )
    store.initialize_by_component_configer(types.SimpleNamespace())
    return store


def test_segments_are_written_to_the_configured_directory(tmp_path):
    """The advertised persist_directory must contain the database."""
    store = _build_store(tmp_path / "cold")

    store.add(
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

    assert (tmp_path / "cold" / "chroma.sqlite3").is_file(), (
        "nothing was written to persist_directory, so the client is in-memory"
    )
    assert store._chroma_client._system.settings.is_persistent is True


def test_two_stores_with_different_directories_coexist(tmp_path):
    """Two cold stores in one process must not fight over one global system."""
    first = _build_store(tmp_path / "first", collection_name="first")
    second = _build_store(tmp_path / "second", collection_name="second")

    for store in (first, second):
        store.add(
            [
                ContextSegment(
                    id="segment-1",
                    type=ContextType.CONVERSATION,
                    priority=ContextPriority.HIGH,
                    content="archived context",
                    tokens=2,
                )
            ],
            session_id="shared-session",
        )

    assert first.get(session_id="shared-session")[0].content == "archived context"
    assert second.get(session_id="shared-session")[0].content == "archived context"
    assert (tmp_path / "first" / "chroma.sqlite3").is_file()
    assert (tmp_path / "second" / "chroma.sqlite3").is_file()
