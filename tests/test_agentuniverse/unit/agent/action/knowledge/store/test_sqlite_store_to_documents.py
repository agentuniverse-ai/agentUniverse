from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def test_to_documents_reads_metadata_from_query_result():
    result = SQLiteStore.to_documents({
        "ids": [["doc-1"]],
        "documents": [["hello"]],
        "metadatas": [[{"source": "test"}]],
    })

    assert result[0].id == "doc-1"
    assert result[0].text == "hello"
    assert result[0].metadata == {"source": "test"}


def test_to_documents_allows_missing_metadata_and_empty_results():
    without_metadata = SQLiteStore.to_documents({
        "ids": [["doc-1"]],
        "documents": [["hello"]],
        "metadatas": None,
    })

    assert without_metadata[0].metadata is None
    assert SQLiteStore.to_documents({"ids": [[]], "documents": [[]]}) == []
