from unittest.mock import patch

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class SuccessfulStore:
    def query(self, query):
        return [Document(id="doc-1", text=f"result for {query.query_str}")]


class FailingStore:
    def query(self, query):
        raise RuntimeError(f"{query.query_str} store is offline")  # noqa: TRY003


def make_knowledge():
    return Knowledge(name="diagnostic_knowledge", stores=["ok", "offline"])


def test_query_diagnostics_report_success_and_partial_failure():
    knowledge = make_knowledge()
    routes = [(Query(query_str="q"), "ok"), (Query(query_str="q"), "offline")]
    stores = {"ok": SuccessfulStore(), "offline": FailingStore()}

    with (
        patch.object(knowledge, "_route_rag", return_value=routes),
        patch.object(knowledge, "_channel_fusion_enabled", return_value=False),
        patch.object(knowledge, "_rag_post_process", side_effect=lambda docs, _: docs),
        patch("agentuniverse.agent.action.knowledge.knowledge.StoreManager") as store_manager,
    ):
        store_manager.return_value.get_instance_obj.side_effect = lambda code, **_: stores[code]
        result = Knowledge.query_knowledge_with_diagnostics.__wrapped__(
            knowledge,
            query_str="q",
        )

    assert [document.id for document in result.documents] == ["doc-1"]
    assert [item.store_code for item in result.diagnostics] == ["ok", "offline"]
    assert result.diagnostics[0].succeeded is True
    assert result.diagnostics[0].document_count == 1
    assert result.diagnostics[0].duration_ms >= 0
    assert result.diagnostics[0].error is None
    assert result.diagnostics[1].succeeded is False
    assert result.diagnostics[1].document_count == 0
    assert result.diagnostics[1].duration_ms >= 0
    assert result.diagnostics[1].error == "RuntimeError: q store is offline"


def test_existing_query_api_still_returns_only_documents():
    knowledge = make_knowledge()
    expected = [Document(id="doc-1", text="result")]

    with patch.object(
        knowledge,
        "_query_knowledge_with_diagnostics",
    ) as query_with_diagnostics:
        query_with_diagnostics.return_value.documents = expected
        result = Knowledge.query_knowledge.__wrapped__(knowledge, query_str="q")

    assert result == expected
