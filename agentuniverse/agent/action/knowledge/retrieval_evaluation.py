"""Offline evaluation of configured Knowledge pipelines against supplied labels.

No synthetic relevance inference, LLM judge or application bootstrap occurs.
Callers own the initialized pipelines and their executor lifetimes.
"""

import hashlib
import json
import math
import time
from typing import Any, Dict, List, Mapping


def _positive_int(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _labels(judgments):
    if not isinstance(judgments, dict):
        raise ValueError("judgments must be a document-ID to grade mapping")
    for identity, grade in judgments.items():
        if not isinstance(identity, str) or not identity:
            raise ValueError("judgment IDs must be nonempty strings")
        if type(grade) is not int or not 0 <= grade <= 30:
            raise ValueError("relevance grades must be integers from 0 to 30")


def ranking_metrics(document_ids: List[str], judgments: Dict[str, int], k: int) -> Dict[str, float]:
    """Calculate Recall@k, MRR@k and exponential-gain nDCG@k.

    Preserve supplied order. Duplicate IDs occupy ranks but receive gain only
    at their first occurrence. Unjudged IDs are nonrelevant. No-positive-label
    queries have zero metrics, rather than being removed from averages.
    """
    _positive_int(k, "k")
    _labels(judgments)
    if not isinstance(document_ids, list) or any(not isinstance(x, str) or not x for x in document_ids):
        raise ValueError("document_ids must be a list of nonempty strings")
    seen = set()
    hits = 0
    reciprocal = 0.0
    dcg = 0.0
    for rank, identity in enumerate(document_ids[:k], 1):
        grade = judgments.get(identity, 0) if identity not in seen else 0
        seen.add(identity)
        if grade:
            hits += 1
            if not reciprocal:
                reciprocal = 1.0 / rank
            dcg += (2 ** grade - 1) / math.log2(rank + 1)
    relevant = sum(grade > 0 for grade in judgments.values())
    ideal = sum((2 ** grade - 1) / math.log2(rank + 1)
                for rank, grade in enumerate(sorted(judgments.values(), reverse=True)[:k], 1))
    return {"recall": hits / relevant if relevant else 0.0,
            "mrr": reciprocal, "ndcg": dcg / ideal if ideal else 0.0}


def evaluate_retrieval(pipelines: Mapping[str, Any], cases: List[Dict], *,
                       k: int = 10, provenance: Dict = None,
                       max_cases: int = 1000, max_pipelines: int = 20,
                       baseline: str = None) -> Dict:
    """Run actual ``query_knowledge`` calls and return a JSON-safe report.

    Cases require query_id, query and judgments. Labels are never sent to the
    pipeline. Exceptions count as zero-score queries; only exception type is
    reported, avoiding accidental disclosure of credentials in exception text.
    Pipeline calls are sequential and not cancelled or retried. Configure
    provider/network timeouts on the supplied pipelines. This function cannot
    detect errors that Knowledge itself catches and suppresses.
    """
    for value, name in [(k, "k"), (max_cases, "max_cases"), (max_pipelines, "max_pipelines")]:
        _positive_int(value, name)
    if not isinstance(pipelines, Mapping) or not 0 < len(pipelines) <= max_pipelines:
        raise ValueError("provide between one and max_pipelines pipelines")
    for name, pipeline in pipelines.items():
        if not isinstance(name, str) or not name or not callable(getattr(pipeline, "query_knowledge", None)):
            raise ValueError("pipelines require nonempty names and query_knowledge methods")
    if baseline is not None and (not isinstance(baseline, str) or baseline not in pipelines):
        raise ValueError("baseline must name a supplied pipeline")
    if not isinstance(cases, list) or not 0 < len(cases) <= max_cases:
        raise ValueError("provide between one and max_cases cases")
    clean = []
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"query_id", "query", "judgments"}:
            raise ValueError("cases require exactly query_id, query and judgments")
        if not isinstance(case["query_id"], str) or not case["query_id"] or case["query_id"] in seen:
            raise ValueError("query IDs must be unique nonempty strings")
        if not isinstance(case["query"], str) or not case["query"].strip():
            raise ValueError("query must be a nonblank string")
        _labels(case["judgments"])
        seen.add(case["query_id"])
        clean.append({**case, "judgments": dict(case["judgments"])})
    if provenance is not None and not isinstance(provenance, dict):
        raise ValueError("provenance must be a JSON-serializable mapping")
    # Copy and validate provenance before any external pipeline operation.
    provenance_copy = json.loads(json.dumps(provenance or {}, allow_nan=False))
    dataset_hash = hashlib.sha256(json.dumps(clean, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    report = {"schema_version": 1, "k": k, "dataset_sha256": dataset_hash,
              "provenance": provenance_copy, "pipelines": {}}
    for name, pipeline in pipelines.items():
        rows = []
        for case in clean:
            started = time.perf_counter()
            error = None
            ids = []
            try:
                documents = pipeline.query_knowledge(query_str=case["query"], similarity_top_k=k)
                if not isinstance(documents, list):
                    raise TypeError("query_knowledge must return a list")
                ids = [doc.id for doc in documents[:k]]
                metrics = ranking_metrics(ids, case["judgments"], k)
            except Exception as exc:
                error = type(exc).__name__
                ids = []
                metrics = {"recall": 0.0, "mrr": 0.0, "ndcg": 0.0}
            rows.append({"query_id": case["query_id"], "document_ids": ids,
                         "has_positive_labels": any(case["judgments"].values()),
                         "error_type": error, "latency_ms": (time.perf_counter() - started) * 1000,
                         **metrics})
        report["pipelines"][name] = {
            "queries": rows, "query_count": len(rows),
            "error_count": sum(row["error_type"] is not None for row in rows),
            "macro": {metric: sum(row[metric] for row in rows) / len(rows)
                      for metric in ("recall", "mrr", "ndcg", "latency_ms")}}
    if baseline is not None:
        report["comparisons"] = _compare_pipelines(report["pipelines"], baseline)
    return report


def _compare_pipelines(results, baseline):
    """Compare same-run queries without hiding failed or unchanged cases."""
    reference = results[baseline]
    comparisons = {}
    metrics = ("recall", "mrr", "ndcg", "latency_ms")
    for name, candidate in results.items():
        if name == baseline:
            continue
        rows = []
        for before, after in zip(reference["queries"], candidate["queries"]):
            # First occurrence determines rank; duplicate slots still count.
            old_ranks = {}
            new_ranks = {}
            for rank, identity in enumerate(before["document_ids"], 1):
                old_ranks.setdefault(identity, rank)
            for rank, identity in enumerate(after["document_ids"], 1):
                new_ranks.setdefault(identity, rank)
            identities = list(old_ranks) + [key for key in new_ranks if key not in old_ranks]
            rows.append({
                "query_id": before["query_id"],
                "baseline_error_type": before["error_type"],
                "candidate_error_type": after["error_type"],
                "delta": {metric: after[metric] - before[metric] for metric in metrics},
                "ranks": [{"document_id": identity,
                           "baseline_rank": old_ranks.get(identity),
                           "candidate_rank": new_ranks.get(identity)} for identity in identities],
            })
        comparisons[name] = {
            "baseline": baseline, "queries": rows,
            "macro_delta": {metric: candidate["macro"][metric] - reference["macro"][metric]
                            for metric in metrics},
            "outcomes": {metric: {
                "improved": sum(row["delta"][metric] > 0 for row in rows),
                "unchanged": sum(row["delta"][metric] == 0 for row in rows),
                "regressed": sum(row["delta"][metric] < 0 for row in rows),
            } for metric in ("recall", "mrr", "ndcg")},
        }
    return comparisons
