"""Explicit as-of selection and source/chunk preservation."""
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.effective_version_selector import EffectiveVersionSelector as Selector
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def doc(identity, version, start, end=None, logical="policy"):
    return Document(id=identity, text=identity, metadata={"logical_document_id": logical,
        "document_version": version, "valid_from": start, "valid_to": end})


def query(at="2026-02-01T00:00:00Z"):
    return Query(ext_info={"as_of": at})


def test_latest_active_preserves_all_chunks_and_order_without_mutation():
    batch = [doc("old", "v1", "2026-01-01T00:00:00Z"),
             doc("new-2", "v2", "2026-02-01T00:00:00Z"),
             doc("new-1", "v2", "2026-02-01T00:00:00Z")]
    before = [d.model_dump() for d in batch]
    result = Selector().process_docs(batch, query())
    assert result == batch[1:]
    assert result[0] is batch[1]
    assert [d.model_dump() for d in batch] == before
    assert Selector().process_docs(batch, query("2026-01-15T00:00:00Z")) == batch[:1]


@pytest.mark.parametrize("at,expected", [("2025-12-31T23:59:59Z", False),
    ("2026-01-01T00:00:00Z", True), ("2026-02-01T00:00:00Z", False),
    ("2026-01-01T08:00:00+08:00", True)])
def test_interval_boundaries_and_timezone(at, expected):
    batch = [doc("x", "v1", "2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z")]
    assert bool(Selector().process_docs(batch, query(at))) == expected


@pytest.mark.parametrize("timestamp", ["2026-01-01", "2026-01-01T00:00:00", "bad", 1, None, "2026-02-30T00:00:00Z",
    "2026-01-01T00:00:00+00:60", "2026-01-01T00:00:00-01:99"])
def test_invalid_as_of(timestamp):
    with pytest.raises(ValueError):
        Selector().process_docs([], query(timestamp))


def test_missing_policies():
    batch = [Document(text="unknown")]
    assert Selector().process_docs(batch, query()) == []
    with pytest.raises(ValueError):
        Selector(missing="error").process_docs(batch, query())
    with pytest.raises(ValueError):
        Selector().process_docs([], Query())


def test_conflicting_version_metadata_rejected():
    batch = [doc("one", "v1", "2026-01-01T00:00:00Z"), doc("two", "v1", "2026-01-02T00:00:00Z")]
    with pytest.raises(ValueError, match="inconsistent"):
        Selector().process_docs(batch, query())


def test_active_start_tie_rejected():
    batch = [doc("one", "v1", "2026-01-01T00:00:00Z"), doc("two", "v2", "2026-01-01T00:00:00Z")]
    for order in (batch, batch[::-1]):
        with pytest.raises(ValueError, match="same start"):
            Selector().process_docs(order, query())


def test_older_active_ties_rejected_in_every_order():
    from itertools import permutations
    batch = [doc("one", "v1", "2026-01-01T00:00:00Z"),
             doc("two", "v2", "2026-01-01T00:00:00Z"),
             doc("three", "v3", "2026-01-02T00:00:00Z")]
    for order in permutations(batch):
        with pytest.raises(ValueError, match="same start"):
            Selector().process_docs(list(order), query())


def test_distinct_logical_documents_never_collapse():
    batch = [doc("one", "v1", "2026-01-01T00:00:00Z", logical="A"),
             doc("two", "v1", "2026-01-01T00:00:00Z", logical="B")]
    assert Selector().process_docs(batch, query()) == batch


@pytest.mark.parametrize("enabled", [False, True])
def test_public_knowledge_after_sqlite_round_trip(tmp_path, enabled):
    from unittest.mock import MagicMock, patch
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore

    store = SQLiteStore(db_path=str(tmp_path / "versions.db"), keyword_extractor="keywords")
    knowledge = knowledge_module.Knowledge(stores=["local"], post_processors=["effective"] if enabled else [])
    store._new_client()
    try:
        with patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as pm:
            pm.return_value.get_instance_obj.return_value = JiebaKeywordExtractor()
            batch = [doc("old", "v1", "2026-01-01T00:00:00Z"), doc("new", "v2", "2026-02-01T00:00:00Z")]
            for item in batch:
                item.text = "alpha " + item.id
            store.insert_document(batch)
            store.conn.close()
            store._new_client()
            router = MagicMock()
            router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), "local")]
            with patch.object(knowledge_module, "StoreManager") as sm, \
                    patch.object(knowledge_module, "DocProcessorManager") as dm, \
                    patch.object(knowledge_module, "RagRouterManager") as rm, \
                    patch.object(trace_module, "ConversationMemoryModule"), \
                    patch.object(trace_module, "Monitor") as monitor:
                sm.return_value.get_instance_obj.return_value = store
                dm.return_value.get_instance_obj.return_value = Selector()
                rm.return_value.get_instance_obj.return_value = router
                monitor.get_invocation_chain.return_value = []
                old = knowledge.query_knowledge(query_str="alpha", ext_info={"as_of": "2026-01-15T00:00:00Z"})
                new = knowledge.query_knowledge(query_str="alpha", ext_info={"as_of": "2026-02-15T00:00:00Z"})
            assert {d.id for d in old} == ({"old"} if enabled else {"old", "new"})
            assert {d.id for d in new} == ({"new"} if enabled else {"old", "new"})
    finally:
        knowledge.insert_executor.shutdown(wait=True)
        knowledge.query_executor.shutdown(wait=True)
        store.conn.close()


def test_yaml_configuration_resolution():
    import importlib
    from pathlib import Path
    import yaml
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    root = Path(__file__).resolve().parents[7]
    data = yaml.safe_load((root / "agentuniverse/agent/action/knowledge/doc_processor/effective_version_selector.yaml").read_text(encoding="utf-8"))
    cls = getattr(importlib.import_module(data["metadata"]["module"]), data["metadata"]["class"])
    config = ComponentConfiger()
    for key, value in data.items():
        if key != "metadata":
            setattr(config, key, value)
    assert cls()._initialize_by_component_configer(config).missing == "exclude"


@pytest.mark.parametrize("options", [
    {"document_key": " "}, {"version_key": "logical_document_id"},
    {"as_of_key": ""}, {"missing": "ignore"}, {"start_key": 3},
])
def test_invalid_configuration_does_not_partially_change_existing_selector(options):
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    config = ComponentConfiger()
    for key, value in options.items():
        setattr(config, key, value)
    selector = Selector(missing="error")
    before = selector.model_dump()
    with pytest.raises(ValueError):
        selector._initialize_by_component_configer(config)
    assert selector.model_dump() == before


@pytest.mark.parametrize("enabled", [False, True])
def test_registered_yaml_public_query_preserves_as_of(tmp_path, enabled):
    from pathlib import Path
    from unittest.mock import patch
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager

    managers = [StoreManager(), DocProcessorManager(), RagRouterManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous_app = apps.app_configer
    except ValueError:
        previous_app = None
    settings = Configer()
    settings.value = {"BASE_INFO": {"appname": "effective-version-integration"}}
    store = knowledge = None
    try:
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        config = ComponentConfiger().load_by_configer(Configer(str(
            root / "agentuniverse/agent/action/knowledge/doc_processor/effective_version_selector.yaml"
        )).load())
        assert config.get_component_config_type() == "DOC_PROCESSOR"
        selector = Selector().initialize_by_component_configer(config)
        keywords = JiebaKeywordExtractor(name="keywords")
        router = BaseRouter(name="base_router")
        store = SQLiteStore(name="local", db_path=str(tmp_path / "registered.db"),
                            keyword_extractor="keywords")
        store._new_client()
        for manager, component in [(managers[0], store), (managers[1], selector),
                                   (managers[1], keywords), (managers[2], router)]:
            manager.register(component.get_instance_code(), component)
        first = managers[1].get_instance_obj("effective_version_selector", strict=True)
        second = managers[1].get_instance_obj("effective_version_selector", strict=True)
        assert first is not second
        first.missing = "error"
        assert second.missing == "exclude"
        batch = [doc("old", "v1", "2026-01-01T00:00:00Z"),
                 doc("new-a", "v2", "2026-02-01T00:00:00Z"),
                 doc("new-b", "v2", "2026-02-01T00:00:00Z")]
        for item in batch:
            item.text = "alpha " + item.id
        store.insert_document(batch)
        store.conn.close()
        store._new_client()
        knowledge = Knowledge(stores=["local"],
                              post_processors=["effective_version_selector"] if enabled else [])
        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            for at, expected in [("2026-01-15T00:00:00Z", {"old"}),
                                 ("2026-02-01T08:00:00+08:00", {"new-a", "new-b"})]:
                result = knowledge.query_knowledge(query_str="alpha", keywords={"alpha"},
                                                   ext_info={"as_of": at}, similarity_top_k=10)
                assert {item.id for item in result} == (expected if enabled else {d.id for d in batch})
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous_app
