"""Independent SciFact labels, fixed lexical recall, no tuning.

Run: python -m examples.bm25_scifact_evaluation /path/to/scifact.zip
Dataset archive stays outside the PR; output contains IDs/metrics, not source text.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def index(texts):
    counts = {key: Counter(re.findall(r"\w+", text.casefold())) for key, text in texts.items()}
    df = Counter(term for row in counts.values() for term in row)
    idf = {term: math.log((1 + len(counts)) / (1 + count)) + 1 for term, count in df.items()}
    postings = defaultdict(list)
    for key, row in counts.items():
        weights = {term: (1 + math.log(count)) * idf[term] for term, count in row.items()}
        norm = math.sqrt(sum(value * value for value in weights.values()))
        for term, value in weights.items():
            postings[term].append((key, value / norm))
    return idf, postings


def recall(text, search_index):
    idf, postings = search_index
    scores = defaultdict(float)
    for term, count in Counter(re.findall(r"\w+", text.casefold())).items():
        weight = (1 + math.log(count)) * idf.get(term, 0)
        for key, normalized in postings.get(term, []):
            scores[key] += weight * normalized
    # Query norm is constant within a query; omitting it preserves cosine order.
    return sorted(scores, key=lambda key: (-scores[key], key))[:100]


def metrics(ids, relevant):
    gains = [int(key in relevant) for key in ids[:10]]
    ideal = sum(1 / math.log2(rank + 2) for rank in range(min(10, len(relevant))))
    return {
        "recall_at_10": sum(gains) / len(relevant),
        "mrr_at_10": next((1 / (rank + 1) for rank, gain in enumerate(gains) if gain), 0),
        "ndcg_at_10": sum(gain / math.log2(rank + 2) for rank, gain in enumerate(gains)) / ideal,
    }


def evaluate(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165":
        raise ValueError("Unexpected SciFact archive SHA256")
    with zipfile.ZipFile(path) as archive:
        corpus = [json.loads(line) for line in archive.read("scifact/corpus.jsonl").splitlines()]
        queries = {row["_id"]: row["text"] for row in map(json.loads, archive.read("scifact/queries.jsonl").splitlines())}
        qrels = defaultdict(set)
        for row in csv.DictReader(io.StringIO(archive.read("scifact/qrels/test.tsv").decode()), delimiter="\t"):
            if int(row["score"]) > 0:
                qrels[row["query-id"]].add(row["corpus-id"])
    assert len(corpus) == 5183 and len(qrels) == 300
    docs = {row["_id"]: Document(id=row["_id"], text=row["title"] + "\n" + row["text"]) for row in corpus}
    body_index = index({row["_id"]: row["text"] for row in corpus})
    title_index = index({row["_id"]: row["title"] for row in corpus})
    bm25 = BM25Reranker(top_n=None)
    rrf = ReciprocalRankFusionProcessor(channel_key="channel", top_n=None)
    rows = []
    for qid in sorted(qrels):
        query = Query(query_str=queries[qid])
        body, title = recall(queries[qid], body_index), recall(queries[qid], title_index)
        union = list(dict.fromkeys(body + title))
        channels = [docs[key].model_copy(update={"metadata": {"channel": name}})
                    for name, ids in [("body", body), ("title", title)] for key in ids]
        rankings = {
            "original_body_first_union": union,
            "rrf": [doc.id for doc in rrf.process_docs(channels, query)],
            "bm25": [doc.id for doc in bm25.process_docs([docs[key] for key in union], query)],
        }
        assert all(set(ids) == set(union) and len(ids) == len(union) for ids in rankings.values())
        rows.append({"query_id": qid, "candidate_count": len(union),
                     "candidate_recall": len(set(union) & qrels[qid]) / len(qrels[qid]),
                     "metrics": {name: metrics(ids, qrels[qid]) for name, ids in rankings.items()},
                     "top10": {name: ids[:10] for name, ids in rankings.items()}})
    aggregates = {name: {metric: sum(row["metrics"][name][metric] for row in rows) / len(rows)
                         for metric in rows[0]["metrics"][name]} for name in rows[0]["metrics"]}
    changes = {}
    for baseline in ("original_body_first_union", "rrf"):
        differences = [row["metrics"]["bm25"]["ndcg_at_10"] - row["metrics"][baseline]["ndcg_at_10"] for row in rows]
        changes[baseline] = {"improved": sum(d > 1e-12 for d in differences),
                             "worsened": sum(d < -1e-12 for d in differences),
                             "unchanged": sum(abs(d) <= 1e-12 for d in differences)}
    return {"dataset": "BEIR SciFact test", "archive_sha256": digest,
            "corpus_count": len(corpus), "query_count": len(rows),
            "protocol": "Fixed body/title TF-IDF top100 union; original body-first, RRF k60, BM25 k1=1.2 b=.75; no tuning; binary positive qrels; all test queries",
            "candidate_recall": sum(row["candidate_recall"] for row in rows) / len(rows),
            "aggregate": aggregates, "bm25_ndcg_changes": changes, "per_query": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.archive), indent=2))
