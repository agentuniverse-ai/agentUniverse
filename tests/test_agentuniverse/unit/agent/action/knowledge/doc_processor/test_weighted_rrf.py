"""Optional weighted fusion contracts; baseline RRF tests run separately."""
import math
from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor as RRF
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger


def docs():
    return [Document(id=name, text=name, metadata={"channel": channel})
            for channel, names in [("A", ["x", "x", "y"]), ("B", ["y", "x"])]
            for name in names]


def test_exact_scores_duplicate_rank_gaps_and_explanation():
    result = RRF(channel_key="channel", k=0, channel_weights={"A": 2.0}, explain=True).process_docs(docs())
    assert [d.id for d in result] == ["x", "y"]
    assert [d.metadata["relevance_score"] for d in result] == pytest.approx([2.5, 5 / 3])
    for doc in result:
        detail = doc.metadata["fusion_details"]
        assert sum(e["contribution"] for e in detail["channels"]) == doc.metadata["relevance_score"]
    assert result[1].metadata["fusion_details"]["channels"][0]["rank"] == 3


@pytest.mark.parametrize("limit", [0, 1, 2, 10])
def test_bounded_explanations_reconcile(limit):
    for doc in RRF(channel_key="channel", explain=True, max_explanation_channels=limit).process_docs(docs()):
        detail = doc.metadata["fusion_details"]
        assert len(detail["channels"]) <= limit
        assert len(detail["channels"]) + detail["omitted_channels"] == 2
        assert sum(e["contribution"] for e in detail["channels"]) + detail["omitted_contribution"] == pytest.approx(doc.metadata["relevance_score"])


def test_zero_disables_channel_and_all_zero_returns_empty():
    batch = docs()
    result = RRF(channel_key="channel", channel_weights={"A": 0.0}).process_docs(batch)
    assert [d.id for d in result] == ["y", "x"]
    assert result[0] is batch[3]
    assert RRF(channel_key="channel", channel_weights={"A": 0.0, "B": 0.0}).process_docs(docs()) == []


def test_default_matches_explicit_unit_weights_and_unknown_unused():
    baseline = RRF(channel_key="channel").process_docs(docs())
    explicit = RRF(channel_key="channel", channel_weights={"A": 1.0, "B": 1.0, "unused": 99.0}).process_docs(docs())
    assert [d.model_dump() for d in baseline] == [d.model_dump() for d in explicit]
    assert all("fusion_details" not in d.metadata for d in baseline)


@pytest.mark.parametrize("channel", [None, 42, "unknown"])
def test_unconfigured_channels_use_one(channel):
    batch = [Document(id="x", text="x", metadata={"channel": channel})]
    result = RRF(channel_key="channel", channel_weights={"A": 9.0}, k=0).process_docs(batch)
    assert result[0].metadata["relevance_score"] == 1


@pytest.mark.parametrize("options", [
    {"channel_weights": {"A": -1.0}}, {"channel_weights": {"A": math.inf}},
    {"channel_weights": {"A": math.nan}}, {"channel_weights": {"A": True}},
    {"channel_weights": {"A": "2"}}, {"channel_weights": {1: 2.0}},
    {"explain": "yes"}, {"max_explanation_channels": -1},
    {"max_explanation_channels": True}, {"explanation_field": " "},
    {"explanation_field": "relevance_score"},
])
def test_bad_options(options):
    with pytest.raises(ValueError):
        RRF(**options)


def test_runtime_mutation_checked_before_output_changes():
    processor = RRF()
    processor.channel_weights["A"] = float("nan")
    batch = docs()
    before = [d.model_dump() for d in batch]
    with pytest.raises(ValueError):
        processor.process_docs(batch)
    assert before == [d.model_dump() for d in batch]


def test_overflow_rejected_before_metadata_writes():
    batch = [Document(id="x", text="x", metadata={"channel": key}) for key in ("A", "B")]
    with pytest.raises(ValueError, match="overflow"):
        RRF(k=0, channel_key="channel", channel_weights={"A": 1.7e308, "B": 1.7e308}).process_docs(batch)
    assert all("relevance_score" not in d.metadata for d in batch)


def test_config_load_and_invalid_update():
    config = ComponentConfiger()
    config.name = "weighted"
    config.description = "example"
    config.channel_weights = {"A": 3.0}
    config.explain = True
    processor = RRF()._initialize_by_component_configer(config)
    assert processor.channel_weights == {"A": 3.0}
    assert processor.explain
    config.channel_weights = {"A": -1.0}
    with pytest.raises(ValueError):
        processor._initialize_by_component_configer(config)
    assert processor.channel_weights == {"A": 3.0}


@pytest.mark.parametrize("weighted", [False, True])
def test_real_sqlite_public_knowledge_fusion(tmp_path, weighted):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.query import Query

    processor = RRF(channel_key="recall_channel", explain=True,
                    channel_weights={"B": 3.0} if weighted else {})
    keywords = JiebaKeywordExtractor()
    stores = {}
    knowledge = None
    with patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as pm:
        pm.return_value.get_instance_obj.return_value = keywords
        try:
            for name, identity in [("A", "a"), ("B", "z")]:
                store = SQLiteStore(db_path=str(tmp_path / f"{name}.db"), keyword_extractor="keywords")
                stores[name] = store
                store._new_client()
                store.insert_document([Document(id=identity, text=f"alpha {identity}", metadata={"source": name})])
                store.conn.close()
                store._new_client()
            knowledge = knowledge_module.Knowledge(stores=list(stores), post_processors=["fusion"])
            router = MagicMock()
            router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), name) for name in stores]
            with patch.object(knowledge_module, "StoreManager") as sm, \
                    patch.object(knowledge_module, "DocProcessorManager") as dm, \
                    patch.object(knowledge_module, "RagRouterManager") as rm, \
                    patch.object(trace_module, "ConversationMemoryModule"), \
                    patch.object(trace_module, "Monitor") as monitor:
                sm.return_value.get_instance_obj.side_effect = lambda name, **kw: stores[name]
                dm.return_value.get_instance_obj.return_value = processor
                rm.return_value.get_instance_obj.return_value = router
                monitor.get_invocation_chain.return_value = []
                result = knowledge.query_knowledge(query_str="alpha")
            assert [d.id for d in result] == (["z", "a"] if weighted else ["a", "z"])
            for doc in result:
                assert doc.metadata["fusion_details"]["channels"][0]["channel"] == doc.metadata["source"]
                assert doc.metadata["fusion_details"]["channels"][0]["contribution"] == doc.metadata["relevance_score"]
        finally:
            if knowledge:
                knowledge.insert_executor.shutdown(wait=True)
                knowledge.query_executor.shutdown(wait=True)
            for store in stores.values():
                store.conn.close()


@pytest.mark.parametrize("mode", ["default", "unit", "weighted"])
def test_registered_yaml_public_pipeline_and_counterexample(tmp_path, mode):
    from pathlib import Path
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager

    managers = [StoreManager(), DocProcessorManager(), RagRouterManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    try:
        previous_app = apps.app_configer
    except ValueError:
        previous_app = None
    stores = []
    knowledge = None
    try:
        settings = Configer()
        settings.value = {"BASE_INFO": {"appname": "weighted-rrf-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(settings)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        config = ComponentConfiger().load_by_configer(Configer(str(root /
            "agentuniverse/agent/action/knowledge/doc_processor/reciprocal_rank_fusion_processor.yaml")).load())
        assert config.channel_weights == {} and config.explain is False
        if mode != "default":
            config.channel_weights = {"A": 1.0, "B": 3.0 if mode == "weighted" else 1.0}
            config.explain = mode == "weighted"
        processor = RRF().initialize_by_component_configer(config)
        managers[1].register(processor.get_instance_code(), processor)
        first = managers[1].get_instance_obj("reciprocal_rank_fusion_processor", strict=True)
        second = managers[1].get_instance_obj("reciprocal_rank_fusion_processor", strict=True)
        first.channel_weights["copy-only"] = 9.0
        assert "copy-only" not in second.channel_weights
        keywords = JiebaKeywordExtractor(name="keywords")
        managers[1].register(keywords.get_instance_code(), keywords)
        router = BaseRouter(name="base_router")
        managers[2].register(router.get_instance_code(), router)
        # Hand-authored labels: A is useful for alpha, B for beta. Upweighting B
        # must expose the alpha regression as well as the beta improvement.
        fixtures = {"A": [("a", "alpha useful"), ("b", "beta outdated")],
                    "B": [("z", "alpha unrelated"), ("y", "beta useful")]}
        for name, rows in fixtures.items():
            store = SQLiteStore(name=name, db_path=str(tmp_path / (name + ".db")), keyword_extractor="keywords")
            stores.append(store)
            store._new_client()
            store.insert_document([Document(id=identity, text=text, metadata={"source": name}) for identity, text in rows])
            store.conn.close()
            store._new_client()
            managers[0].register(store.get_instance_code(), store)
        knowledge = Knowledge(stores=["A", "B"], post_processors=["reciprocal_rank_fusion_processor"])
        results = {}
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            for term in ("alpha", "beta"):
                results[term] = knowledge.query_knowledge(query_str=term, keywords={term})
        assert [item.id for item in results["alpha"]] == (["z", "a"] if mode == "weighted" else ["a", "z"])
        assert [item.id for item in results["beta"]] == (["y", "b"] if mode == "weighted" else ["b", "y"])
        hits = {term: result[0].id == relevant for (term, result), relevant in zip(results.items(), ("a", "y"))}
        assert hits == ({"alpha": False, "beta": True} if mode == "weighted" else {"alpha": True, "beta": False})
        for result in results.values():
            for item in result:
                expected_weight = 3.0 if mode == "weighted" and item.metadata["source"] == "B" else 1.0
                assert item.metadata["relevance_score"] == pytest.approx(expected_weight / 61)
                if mode == "weighted":
                    detail = item.metadata["fusion_details"]
                    assert detail["channels"][0]["channel"] == item.metadata["source"]
                    assert detail["channels"][0]["contribution"] == item.metadata["relevance_score"]
                else:
                    assert "fusion_details" not in item.metadata
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        for store in stores:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous_app
