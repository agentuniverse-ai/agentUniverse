"""Opt-in round trips against an expendable, unauthenticated Neo4j database.

Set AU_NEO4J_METADATA_TEST_URI to the local test server's Bolt URI. Only nodes
with a fresh per-test UUID are created/deleted; no existing nodes are touched.
"""

import json
import os
import uuid

import pytest

neo4j = pytest.importorskip("neo4j")
pytest.importorskip("pandas")

from agentuniverse.agent.action.knowledge.store.document import Document  # noqa: E402
from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore  # noqa: E402


@pytest.fixture
def live_store():
    """Connect only when the dedicated integration-test URI is provided."""
    uri = os.environ.get("AU_NEO4J_METADATA_TEST_URI")
    if not uri:
        pytest.skip("AU_NEO4J_METADATA_TEST_URI is not set")
    driver = neo4j.GraphDatabase.driver(uri, auth=None)
    document_id = "au-metadata-test-" + str(uuid.uuid4())
    try:
        driver.verify_connectivity()
        yield Neo4jStore(driver=driver), document_id
    finally:
        try:
            with driver.session() as session:
                session.run("MATCH (d:Document {id: $id}) DELETE d", id=document_id).consume()
        finally:
            driver.close()


@pytest.mark.parametrize("method", ["insert_document", "upsert_document", "update_document"])
@pytest.mark.parametrize("metadata", [
    {},
    {"source": "report", "page": 2},
    {"标题": "收益报告", "nested": {"tags": ["alpha", None, 3, True]}},
    None,
])
def test_metadata_round_trip_and_replacement(live_store, method, metadata):
    """Replace an existing node's metadata and read it through the store API."""
    store, document_id = live_store
    with store.driver.session() as session:
        session.run("CREATE (:Document {id: $id, text: 'old', metadata: $metadata})",
                    id=document_id, metadata='{"old": true}').consume()
    getattr(store, method)([Document(id=document_id, text="新正文", metadata=metadata)])
    rows = store.execute_cypher(
        "MATCH (d:Document {id: $id}) RETURN d.text AS text, d.metadata AS metadata",
        {"id": document_id},
    )
    assert len(rows) == 1
    assert rows.iloc[0]["text"] == "新正文"
    value = rows.iloc[0]["metadata"]
    assert (json.loads(value) if value is not None else None) == metadata


@pytest.mark.parametrize("method", ["insert_document", "upsert_document"])
def test_create_with_nested_metadata(live_store, method):
    """Create a new node rather than only testing MERGE's match branch."""
    store, document_id = live_store
    metadata = {"source": {"pages": [1, 2]}, "active": True}
    getattr(store, method)([Document(id=document_id, text="new", metadata=metadata)])
    rows = store.execute_cypher(
        "MATCH (d:Document {id: $id}) RETURN d.metadata AS metadata", {"id": document_id})
    assert len(rows) == 1
    assert json.loads(rows.iloc[0]["metadata"]) == metadata


def test_update_does_not_create_missing_document(live_store):
    """Encoding must not turn MATCH-based updates into upserts."""
    store, document_id = live_store
    store.update_document([Document(id=document_id, text="missing", metadata={"page": 1})])
    rows = store.execute_cypher(
        "MATCH (d:Document {id: $id}) RETURN count(d) AS total", {"id": document_id})
    assert rows.iloc[0]["total"] == 0
