# Offline ColBERT late-interaction reranking

`ColbertReranker` is an opt-in `DocProcessor` for a bounded set of already retrieved
text documents. It computes one vector per token and scores with MaxSim: sum each
query token's best document-token dot product. It is not mean pooling, a cross
encoder, BM25, RRF, a vector database or a new ingestion pipeline.
The model-specific prefixes, document punctuation mask and 32-position query
expansion come from the fixed Sentence Transformers profile, not a hand-written
approximation. See [Sentence Transformers](https://sbert.net/docs/multi_vector_encoder/usage/usage.html).

## Install and cache once

The optional `colbert_ext` extra pins Sentence Transformers 6.2.0 and requires
PyTorch >=2.6,<3. Tests use torch 2.6.0 on CPU. The first supported profile is the
English [Answer.AI small ColBERT model](https://huggingface.co/answerdotai/answerai-colbert-small-v1)
(Apache-2.0), revision `934fa8bb4ce2284f4c2baa232d81aca4d076fa5e`.
Weights are not included in this repository. To populate the public model cache:

```sh
pip install 'sentence-transformers==6.2.0' 'torch>=2.6,<3'
python -c "from sentence_transformers import MultiVectorEncoder; MultiVectorEncoder('answerdotai/answerai-colbert-small-v1', revision='934fa8bb4ce2284f4c2baa232d81aca4d076fa5e', device='cpu', trust_remote_code=False, token=False)"
```

Use the same environment/cache directory at runtime. The processor always uses
`local_files_only=True`, `trust_remote_code=False`, and `token=False`; a missing
cache raises an error, never silently downloads or falls back to lexical scores.
With a SOCKS proxy, install the `socksio` dependency for the cache-preparation
step. A base install can import the processor without loading torch or a model.

## Register and use

Copy `agentuniverse/agent/action/knowledge/doc_processor/colbert_reranker.yaml.example`
to your configured doc_processor package with a `.yaml` suffix. The example is
not auto-registered, so the optional dependency/model is never loaded by default.
Then add `post_processors: [colbert_reranker]` to an existing Knowledge component
whose store already retrieves relevant candidates. Registering the processor does
not create a store, embedding or index; it cannot recover a document absent from
the candidate list.

```python
from agentuniverse.agent.action.knowledge.doc_processor.colbert_reranker import ColbertReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query

ranker = ColbertReranker(top_n=2)
docs, receipt = ranker.rerank(
    [Document(text="A cat purrs."), Document(text="A dog barks.")],
    Query(query_str="Which animal barks?"),
)
# process_docs(candidates, query) returns only documents for the Knowledge pipeline.
```

Returned documents retain text, IDs, keywords and ordinary one-dimensional
embeddings. Metadata is deep-copied and `colbert_rerank` records score, rank,
original candidate position and model revision. Reranking twice replaces that
processor-owned metadata namespace. Ties preserve input order. The receipt gives
input token counts, actual vector counts, scores, revision and `truncated=False`.

## Bounds and limitations

Defaults: 32 candidates, batch size 4, top_n 5, query 1,000 characters,
each document 4,000 characters, total input 64,000 characters. Profile limits are
32 query tokens (including prompt/special tokens) and 300 document tokens. Inputs
over any limit fail **before encoding**, instead of being silently truncated.
Query expansion still emits 32 vectors. Raw character limits bound tokenization;
per-document interaction is capped at 9,600 cells before inference and checked
again when scoring. Document encoding is batched, scoring is per document; these
are workload bounds, not a promise about whole-process resident memory.

Only this fixed English text profile and CPU inference are supported initially.
No GPU, arbitrary checkpoint, multilingual quality, image input, token-vector
index, persistent embedding cache, online model API or throughput claim is made.
Each instance serializes encoding with a lock; concurrent calls do not share
mutable result lists or overwrite the caller's documents. The underlying model
remains resident after its first use.

## Evidence

The checked-in runner in `tests/reproduction/colbert-late-interaction/` exercises
the real fixed-revision model, the public YAML/manager/SQLite/Knowledge path,
exact arithmetic versus official `encoder.similarity` and an independent scalar
MaxSim oracle, stable ties, metadata isolation, and rejected inputs before model
loading/encoding. Nine existing processor-pipeline regressions are also included.

A 3-query/12-document authored English fixture compares ranks with `rank-bm25`.
This is a controlled smoke experiment, not a representative benchmark or proof
of quality superiority. Per-query reciprocal ranks, NDCG@10, CPU elapsed times
and score-matrix sizes are recorded in JUnit, together with process RSS snapshots
before/after each warm-model call (not a component-only allocation or peak-memory
measurement). Model download/load time is excluded from those warm-call times.
One query's relevant document was
ranked second, not first; no claim of perfect retrieval is made. See the evidence
README for actual environment/result details. No hosted CI, merge or score claim.
