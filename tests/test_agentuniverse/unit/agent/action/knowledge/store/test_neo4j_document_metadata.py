"""Document metadata must be a supported Neo4j property value."""

from copy import deepcopy
import json
from unittest.mock import MagicMock

import pytest

pytest.importorskip("neo4j")
pytest.importorskip("pandas")

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore


WRITE_METHODS = ("insert_document", "upsert_document", "update_document")


@pytest.fixture
def store():
    """Use a recording driver; serialization must happen before database I/O."""
    return Neo4jStore(driver=MagicMock())


@pytest.mark.parametrize("method", WRITE_METHODS)
@pytest.mark.parametrize("metadata", [
    None,
    {},
    {"source": "report", "page": 2},
    {"标题": "收益报告", "nested": {"tags": ["alpha", None, 3, True]}, "ratio": 1.5},
])
def test_write_serializes_metadata_without_mutating_documents(store, method, metadata):
    """All write entry points retain JSON values, including an empty object."""
    doc = Document(id="document-1", text="原文", metadata=metadata)
    original = deepcopy(doc.model_dump())

    getattr(store, method)([doc])

    session = store.driver.session.return_value
    session.run.assert_called_once()
    parameters = session.run.call_args.kwargs
    assert parameters["id"] == doc.id
    assert parameters["text"] == doc.text
    if metadata is None:
        assert parameters["metadata"] is None
    else:
        assert isinstance(parameters["metadata"], str)
        assert json.loads(parameters["metadata"]) == metadata
        if "标题" in metadata:
            assert "收益报告" in parameters["metadata"]
    assert doc.model_dump() == original
    session.close.assert_called_once_with()


@pytest.mark.parametrize("method", WRITE_METHODS)
def test_multiple_documents_keep_their_own_metadata(store, method):
    """Serialize each document, not one shared batch value."""
    docs = [Document(text="one", metadata={"page": 1}),
            Document(text="two", metadata={"page": 2})]
    getattr(store, method)(docs)
    calls = store.driver.session.return_value.run.call_args_list
    assert [json.loads(call.kwargs["metadata"]) for call in calls] == [
        {"page": 1}, {"page": 2}]


@pytest.mark.parametrize("method", WRITE_METHODS)
@pytest.mark.parametrize("invalid", [{1, 2}, float("nan"), float("inf")])
def test_invalid_metadata_is_rejected_before_any_batch_write(store, method, invalid):
    """A later invalid document must not leave the earlier document written."""
    docs = [Document(text="valid", metadata={"page": 1}),
            Document(text="invalid", metadata={"value": invalid})]
    with pytest.raises(ValueError, match="JSON-serializable"):
        getattr(store, method)(docs)
    store.driver.session.assert_not_called()


@pytest.mark.parametrize("method", WRITE_METHODS)
def test_write_errors_still_propagate_and_close_session(store, method):
    """Encoding must not hide errors raised by the existing write path."""
    session = store.driver.session.return_value
    error = RuntimeError("database unavailable")
    session.run.side_effect = error
    with pytest.raises(RuntimeError) as caught:
        getattr(store, method)([Document(text="one", metadata={"page": 1})])
    assert caught.value is error
    session.close.assert_called_once_with()
