"""Run from repository root: python -m docs.examples.retrieval_evaluation_demo.

Hand-authored rankings demonstrate report interpretation, NOT retrieval quality.
Replace RecordedRanking with initialized Knowledge objects for real evaluation.
"""
import json
from types import SimpleNamespace

from agentuniverse.agent.action.knowledge.retrieval_evaluation import evaluate_retrieval


class RecordedRanking:
    def __init__(self, rankings):
        self.rankings = rankings

    def query_knowledge(self, query_str, similarity_top_k):
        return [SimpleNamespace(id=identity)
                for identity in self.rankings[query_str][:similarity_top_k]]


def main():
    cases = [
        {"query_id": "installation", "query": "AX-12 installation",
         "judgments": {"installation-manual": 2, "product-overview": 1}},
        {"query_id": "voltage", "query": "AX-12 voltage",
         "judgments": {"electrical-spec": 2}},
        {"query_id": "unanswerable", "query": "AX-12 underwater use",
         "judgments": {}},
    ]
    baseline = RecordedRanking({
        "AX-12 installation": ["product-overview", "installation-manual"],
        "AX-12 voltage": ["electrical-spec", "product-overview"],
        "AX-12 underwater use": [],
    })
    candidate = RecordedRanking({
        "AX-12 installation": ["installation-manual", "product-overview"],
        "AX-12 voltage": ["product-overview", "electrical-spec"],
        "AX-12 underwater use": [],
    })
    report = evaluate_retrieval(
        {"baseline": baseline, "candidate": candidate}, cases, k=2,
        baseline="baseline", provenance={"fixture": "hand-authored-report-demo",
                                         "production_benchmark": False})
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
