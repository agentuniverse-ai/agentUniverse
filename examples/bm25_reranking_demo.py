"""Run from the repository root: python -m examples.bm25_reranking_demo.

Offline, hand-authored examples, not an independent relevance benchmark.
No server, database, model, API key or output file is required.
"""

import json
from pathlib import Path

from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def run_demo():
    """Compare fixed candidate orders with RRF and shipped-YAML BM25 settings."""
    yaml_path = Path(__file__).resolve().parents[1] / (
        "agentuniverse/agent/action/knowledge/doc_processor/bm25_reranker.yaml"
    )
    config = ComponentConfiger().load_by_configer(Configer(path=str(yaml_path)).load())
    reranker = BM25Reranker().initialize_by_component_configer(config)
    cases = [
        ("exact_identifier", "AX-12", ["AX-120 manual", "AX-12 manual", "repair guide"], "1"),
        ("semantic_counterexample", "car repair", ["automobile servicing", "car repair invoice", "weather"], "0"),
    ]
    results = []
    for name, query_text, texts, relevant in cases:
        docs = [Document(id=str(i), text=text, metadata={"channel": "first"})
                for i, text in enumerate(texts)]
        query = Query(query_str=query_text)
        # The second controlled channel agrees only on the first candidate.
        second = docs[0].model_copy(update={"metadata": {"channel": "second"}})
        fused = ReciprocalRankFusionProcessor(channel_key="channel").process_docs(docs + [second], query)
        ranked = reranker.process_docs(docs, query)
        rankings = {"original": docs, "rrf": fused, "bm25": ranked}
        results.append({
            "case": name,
            "query": query_text,
            "relevant_id": relevant,
            "candidates": [{"id": doc.id, "text": doc.text} for doc in docs],
            "rankings": {key: [doc.id for doc in value] for key, value in rankings.items()},
            "recall_at_1": {key: int(value[0].id == relevant) for key, value in rankings.items()},
        })
    return {"scope": "hand_authored_examples_not_a_quality_benchmark", "cases": results}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
