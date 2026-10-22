# Neo4j evidence paths / Neo4j 有界证据路径

`Neo4jEvidenceStore` is a read-only, programmatically initialized Store over a
caller-owned Neo4j Driver. It discovers simple paths from an exact entity ID,
retaining the declared document IDs on every edge. It does not accept caller
Cypher, invoke an LLM, or interpret reachability as causality. Existing Neo4jStore
and its document CRUD/metadata serialization are unchanged.

Graph contract: nodes have label `EvidenceEntity`, nonempty string `entity_id`,
and an optional JSON-compatible display `name`. Relationships have a type in the
caller's explicit `relationship_types` list and `source_doc_ids`, a nonempty list
of nonempty strings. Display names are not identities. Enforce unique entity_id
in your schema; multiple matching roots raise. Relationship source/target element
IDs are retained so incoming/undirected traversal cannot reverse a declared claim.
Missing/malformed source declarations are omitted and counted. Source IDs are
**declared references, not verified quotations or proof that the documents exist**.
The application should resolve them against its own source store before citation.

```python
from neo4j import GraphDatabase
from agentuniverse.agent.action.knowledge.store.neo4j_evidence_store import Neo4jEvidenceStore
from agentuniverse.agent.action.knowledge.store.query import Query
with GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','your-password')) as driver:
    store = Neo4jEvidenceStore(name='evidence_paths', client=driver,
        relationship_types=['CITES'], direction='outgoing',
        max_hops=2, max_edges=100, max_nodes=50, max_paths=25)
    docs, report = store.query_with_report(Query(ext_info={'entity_id':'entity-123'}))
    # Register store with StoreManager via store.get_instance_code() if using Knowledge.
```

Roots/relationship types are parameters; direction selects one of three fixed
patterns. Every returned Document has `evidence_path` and `path_report`. This
retains `bounded_partial` status even through Knowledge.query_knowledge. An empty
result can mean no root, no sourced edges or a budget cutoff: use query_with_report
to distinguish these. Database/driver errors propagate from the Store; the existing
Knowledge error-handling policy remains unchanged.

Traversal is BFS with no repeated node in a path. Parallel edges are retained as
different evidence paths; nodes sharing names remain distinct. Adjacencies are
cached per request, avoiding repeated database queries for the same expanded node.
Ordering uses Neo4j element IDs, stable only within the current graph instance;
restoring/recreating a database may change these IDs and result document IDs.
Each partial path of length 1..max_hops is a result. A path limit (or explicit
similarity_top_k in 1..max_paths) stops further enumeration conservatively; hitting
the exact cap is reported as partial even when no further paths might exist.

`max_edges` bounds retained adjacency rows across expansions. One extra row may
be fetched as an overflow sentinel; `rows_retained` does not count that sentinel.
`max_nodes` bounds distinct admitted nodes, `max_paths` output paths and
`max_context_chars` rendered path characters. Counters for missing sources/cycles
refer to traversal decisions, not necessarily unique graph relationships.
`complete_within_hops` means enumeration finished within configured depth; it does
not claim complete graph evidence or that omitted unsourced edges were verified.

These bounds do not cap server-side degree scans/sorts, returned property sizes,
or network buffering before a row is inspected. A driver read transaction timeout
is configured; use appropriate server resource limits and least-privilege read
credentials. One read transaction is used without automatic retries; isolation is
Neo4j's server guarantee, not an application snapshot across external source stores.
Sessions and transactions close on success/failure; the caller owns Driver lifetime.
Async query uses a worker thread, so cancelling the await cannot kill in-flight I/O.
Programmatic initialization is deliberate: no new credential/YAML driver lifecycle.

中文：从明确实体 ID 沿指定关系与方向返回有限简单路径，每条边保留图中声明的
来源文档 ID。显示名称不作为身份；循环不重复节点，多边保留。缺来源边会省略并
报告，来源 ID 不等于已核验的原文。结果附带完整/部分状态，可经 Knowledge 返回。
行/节点/路径/输出预算不等于服务端扫描资源硬上限；可达性不代表因果。

## Real-backend verification

Neo4j Community 5.26.0, driver 5.25.0, disposable loopback-only Linux server.
Set AU_EVIDENCE_NEO4J_URI to its bolt URL and run:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q --import-mode=importlib \
  tests/test_agentuniverse/integration/test_neo4j_evidence_live.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_rrf_integration.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_registration_errors.py \
  tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_reader_lookup.py
```

Fixtures use unique test markers and remove only their own nodes. Tests cover
actual cycles/multiedges/same names, all directions, missing/malformed sources,
budget/empty/error paths, bound parameters, async and Knowledge provenance. They
do not prove quality improvement, source-document validity, distributed snapshot
consistency or compatibility with every Neo4j version. Unlike #4065, this does not
modify document metadata JSON writes; it implements a separate graph schema/query.

Local Windows Python 3.10/3.12 each passed 27 tests with zero skips: 15 real-Neo4j
integration cases and 12 existing Knowledge regressions. Five Pydantic deprecation
warnings appeared in each run. Targeted Ruff E4/E7/E9/F/I, format and diff checks
passed. No hosted CI or source-verification claim is made.
