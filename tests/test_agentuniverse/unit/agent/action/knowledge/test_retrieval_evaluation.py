"""Hand-computed ranking and evaluator failure-accounting contracts."""
import json
import math
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent.action.knowledge.retrieval_evaluation import evaluate_retrieval, ranking_metrics


def case(identity="q"):
    return {"query_id": identity, "query": "alpha", "judgments": {"a": 2, "b": 1}}


def test_hand_computed_metrics():
    scores = ranking_metrics(["unknown", "b", "a"], {"a": 2, "b": 1}, 2)
    assert scores["recall"] == 0.5
    assert scores["mrr"] == 0.5
    assert scores["ndcg"] == pytest.approx((1 / math.log2(3)) / (3 + 1 / math.log2(3)))


def test_duplicate_does_not_gain_or_promote_later_result():
    scores = ranking_metrics(["a", "a", "b"], {"a": 1, "b": 1}, 2)
    assert scores["recall"] == 0.5
    assert scores["ndcg"] == pytest.approx(1 / (1 + 1 / math.log2(3)))


@pytest.mark.parametrize("labels,ids", [({}, []), ({"a": 0}, ["a"]), ({"a": 1}, [])])
def test_empty_and_no_relevant(labels, ids):
    assert ranking_metrics(ids, labels, 3) == {"recall": 0, "mrr": 0, "ndcg": 0}


@pytest.mark.parametrize("grade", [-1, 31, True, 1.5, "2", None])
def test_bad_grades(grade):
    with pytest.raises(ValueError):
        ranking_metrics(["a"], {"a": grade}, 1)


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_bad_cutoff(k):
    with pytest.raises(ValueError):
        ranking_metrics([], {}, k)


def test_errors_count_in_means_and_no_exception_text_leaks():
    pipeline = MagicMock()
    pipeline.query_knowledge.side_effect = [[SimpleNamespace(id="a")], RuntimeError("secret")]
    result = evaluate_retrieval({"test": pipeline}, [case(), case("q2")], k=1)
    data = result["pipelines"]["test"]
    assert data["macro"]["recall"] == 0.25
    assert data["macro"]["mrr"] == 0.5
    assert data["macro"]["ndcg"] == 0.5
    assert data["error_count"] == 1
    assert "secret" not in json.dumps(result)
    assert pipeline.query_knowledge.call_args.kwargs == {"query_str": "alpha", "similarity_top_k": 1}


@pytest.mark.parametrize("bad", [None, [], {}, [SimpleNamespace(id=None)]])
def test_empty_or_invalid_result(bad):
    pipeline = MagicMock()
    pipeline.query_knowledge.return_value = bad
    result = evaluate_retrieval({"test": pipeline}, [case()])
    assert result["pipelines"]["test"]["error_count"] == (0 if bad == [] else 1)


@pytest.mark.parametrize("cases", [[], [case(), case()], [{"query_id": "q"}], [{**case(), "query": " "}]])
def test_invalid_dataset_never_calls_pipeline(cases):
    pipeline = MagicMock()
    with pytest.raises(ValueError):
        evaluate_retrieval({"test": pipeline}, cases)
    pipeline.query_knowledge.assert_not_called()


def test_provenance_detached_and_hash_deterministic():
    pipeline = MagicMock()
    pipeline.query_knowledge.return_value = []
    provenance = {"revision": "local", "nested": [1]}
    first = evaluate_retrieval({"test": pipeline}, [case()], provenance=provenance)
    second = evaluate_retrieval({"test": pipeline}, [case()])
    provenance["nested"].append(2)
    assert first["provenance"]["nested"] == [1]
    assert first["dataset_sha256"] == second["dataset_sha256"]


@pytest.mark.parametrize("baseline", ["missing", [], 1, True])
def test_bad_baseline_never_calls_pipeline(baseline):
    pipeline = MagicMock()
    with pytest.raises(ValueError, match="baseline"):
        evaluate_retrieval({"base": pipeline}, [case()], baseline=baseline)
    pipeline.query_knowledge.assert_not_called()


def test_comparison_retains_duplicate_ranks_and_failed_queries():
    base, candidate = MagicMock(), MagicMock()
    base.query_knowledge.side_effect = [
        [SimpleNamespace(id=x) for x in ["a", "a", "b"]], [], []]
    candidate.query_knowledge.side_effect = [
        [SimpleNamespace(id=x) for x in ["b", "c", "a"]], RuntimeError("secret"), []]
    report = evaluate_retrieval({"base": base, "candidate": candidate},
                                [case(), case("failed"), case("empty")],
                                k=3, baseline="base")
    comparison = report["comparisons"]["candidate"]
    assert comparison["queries"][0]["ranks"] == [
        {"document_id": "a", "baseline_rank": 1, "candidate_rank": 3},
        {"document_id": "b", "baseline_rank": 3, "candidate_rank": 1},
        {"document_id": "c", "baseline_rank": None, "candidate_rank": 2}]
    assert comparison["queries"][1]["candidate_error_type"] == "RuntimeError"
    assert comparison["outcomes"]["ndcg"] == {"improved": 0, "unchanged": 2, "regressed": 1}
    assert comparison["macro_delta"]["recall"] == 0
    assert "secret" not in json.dumps(report, allow_nan=False)


def test_single_baseline_and_default_report_compatibility():
    pipeline = MagicMock()
    pipeline.query_knowledge.return_value = []
    assert "comparisons" not in evaluate_retrieval({"base": pipeline}, [case()])
    assert evaluate_retrieval({"base": pipeline}, [case()], baseline="base")["comparisons"] == {}


def test_documented_example_runs_and_exposes_regression(capsys):
    import runpy
    from pathlib import Path
    example = Path(__file__).resolve().parents[6] / "docs/examples/retrieval_evaluation_demo.py"
    runpy.run_path(str(example), run_name="__main__")
    report = json.loads(capsys.readouterr().out)
    assert report["comparisons"]["candidate"]["outcomes"]["ndcg"] == {
        "improved": 1, "unchanged": 1, "regressed": 1}
    assert report["provenance"]["production_benchmark"] is False


def test_real_knowledge_sqlite_and_rrf_comparison(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.document import Document
    from agentuniverse.agent.action.knowledge.store.query import Query

    store = SQLiteStore(db_path=str(tmp_path / "evaluation.db"), keyword_extractor="keywords")
    pipelines = {"baseline": knowledge_module.Knowledge(stores=["local"]),
                 "rrf": knowledge_module.Knowledge(stores=["local"], post_processors=["rrf"])}
    store._new_client()
    try:
        with patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as pm:
            pm.return_value.get_instance_obj.return_value = JiebaKeywordExtractor()
            store.insert_document([Document(id="a", text="alpha manual", metadata={"source": "fixture"})])
            store.conn.close()
            store._new_client()
            router = MagicMock()
            router.rag_route.side_effect = lambda query, stores: [(Query(query_str=query.query_str, keywords={query.query_str}), "local")]
            with patch.object(knowledge_module, "StoreManager") as sm, \
                    patch.object(knowledge_module, "DocProcessorManager") as dm, \
                    patch.object(knowledge_module, "RagRouterManager") as rm, \
                    patch.object(trace_module, "ConversationMemoryModule"), \
                    patch.object(trace_module, "Monitor") as monitor:
                sm.return_value.get_instance_obj.return_value = store
                dm.return_value.get_instance_obj.return_value = ReciprocalRankFusionProcessor(channel_key="recall_channel")
                rm.return_value.get_instance_obj.return_value = router
                monitor.get_invocation_chain.return_value = []
                report = evaluate_retrieval(pipelines, [
                    {"query_id": "hit", "query": "alpha", "judgments": {"a": 1}},
                    {"query_id": "miss", "query": "absent", "judgments": {"a": 1}},
                ], k=1, provenance={"fixture": "persisted-sqlite"})
            for result in report["pipelines"].values():
                assert result["error_count"] == 0
                assert result["macro"]["recall"] == 0.5
                assert result["macro"]["mrr"] == 0.5
                assert result["macro"]["ndcg"] == 0.5
            json.dumps(report, allow_nan=False)
    finally:
        store.conn.close()
        for pipeline in pipelines.values():
            pipeline.insert_executor.shutdown(wait=True)
            pipeline.query_executor.shutdown(wait=True)
