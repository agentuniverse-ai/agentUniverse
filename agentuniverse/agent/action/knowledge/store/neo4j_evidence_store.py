"""Bounded, provenance-bearing paths from a caller-owned Neo4j graph."""

import asyncio
import hashlib
import json
from collections import deque
from typing import List, Literal

from pydantic import Field

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.store import Store


class Neo4jEvidenceStore(Store):
    """Read paths between EvidenceEntity nodes, retaining declared doc IDs.

    ``client`` is a caller-owned Neo4j Driver. Roots use exact ``entity_id``
    identity, never a display name. Relationship ``source_doc_ids`` must be a
    nonempty list of nonempty strings; unsupported edges are omitted explicitly.
    This component neither generates nor accepts Cypher from a user query.
    """

    database: str = "neo4j"
    relationship_types: List[str] = Field(min_length=1, max_length=50)
    direction: Literal["outgoing", "incoming", "both"] = "outgoing"
    max_hops: int = Field(default=2, strict=True, ge=1, le=6)
    max_edges: int = Field(default=100, strict=True, ge=1, le=10000)
    max_nodes: int = Field(default=50, strict=True, ge=1, le=10000)
    max_paths: int = Field(default=25, strict=True, ge=1, le=10000)
    max_context_chars: int = Field(default=100000, strict=True, ge=1)
    query_timeout: float = Field(default=5, gt=0, le=60, allow_inf_nan=False)

    def query(self, query, **kwargs):
        return self.query_with_report(query)[0]

    async def async_query(self, query, **kwargs):
        return await asyncio.to_thread(self.query, query, **kwargs)

    def query_with_report(self, query):
        """Return simple paths and a bounded-traversal report (not causality)."""
        if self.client is None:
            raise ValueError("Supply a caller-owned Neo4j Driver as client")
        root_id = query.ext_info.get("entity_id")
        if not isinstance(root_id, str) or not root_id:
            raise ValueError("Query.ext_info.entity_id must be an exact nonempty ID")
        if any(not isinstance(t, str) or not t for t in self.relationship_types):
            raise ValueError("relationship_types must contain nonempty strings")
        limit = self.max_paths if query.similarity_top_k is None else query.similarity_top_k
        if type(limit) is not int or not 1 <= limit <= self.max_paths:
            raise ValueError("similarity_top_k must be between 1 and max_paths")
        report = {
            "version": 1,
            "status": "complete_within_hops",
            "rows_retained": 0,
            "missing_sources": 0,
            "invalid_entities": 0,
            "cycles_omitted": 0,
            "limits_reached": [],
            "nodes_seen": 0,
            "paths_returned": 0,
        }
        documents = []
        patterns = {
            "outgoing": "(n)-[r]->(m:EvidenceEntity)",
            "incoming": "(n)<-[r]-(m:EvidenceEntity)",
            "both": "(n)-[r]-(m:EvidenceEntity)",
        }
        statement = (
            "MATCH (n:EvidenceEntity) WHERE elementId(n) = $node "
            f"MATCH {patterns[self.direction]} WHERE type(r) IN $types "
            "RETURN elementId(m) AS key, m.entity_id AS entity_id, m.name AS name, "
            "elementId(r) AS edge_id, type(r) AS relation, r.source_doc_ids AS sources, "
            "elementId(startNode(r)) AS source_key, elementId(endNode(r)) AS target_key "
            "ORDER BY edge_id, key LIMIT $limit"
        )
        with self.client.session(database=self.database, default_access_mode="READ") as session:
            # One read transaction: no writes, no automatic retry side effects in
            # the local accumulation state. Isolation follows the server backend.
            with session.begin_transaction(timeout=self.query_timeout) as tx:
                roots = list(
                    tx.run(
                        "MATCH (n:EvidenceEntity {entity_id: $id}) "
                        "RETURN elementId(n) AS key, n.entity_id AS entity_id, n.name AS name LIMIT 2",
                        id=root_id,
                    )
                )
                if len(roots) > 1:
                    raise ValueError("Ambiguous entity_id; define a uniqueness constraint")
                if not roots:
                    report["status"] = "root_not_found"
                    return [], report
                root = dict(roots[0])
                nodes_seen = {root["key"]}
                queue = deque([([root], [])])
                cache = {}
                chars = 0
                while queue and len(documents) < limit:
                    nodes, edges = queue.popleft()
                    if len(edges) >= self.max_hops:
                        continue
                    key = nodes[-1]["key"]
                    if key not in cache:
                        remaining = self.max_edges - report["rows_retained"]
                        if remaining <= 0:
                            report["limits_reached"].append("edges")
                            break
                        rows = list(tx.run(statement, node=key, types=self.relationship_types, limit=remaining + 1))
                        if len(rows) > remaining:
                            report["limits_reached"].append("edges")
                        cache[key] = [dict(row) for row in rows[:remaining]]
                        report["rows_retained"] += len(cache[key])
                    for row in cache[key]:
                        sources = row["sources"]
                        if (
                            not isinstance(sources, list)
                            or not sources
                            or any(not isinstance(s, str) or not s for s in sources)
                        ):
                            report["missing_sources"] += 1
                            continue
                        if not isinstance(row["entity_id"], str) or not row["entity_id"]:
                            report["invalid_entities"] += 1
                            continue
                        if row["key"] in {node["key"] for node in nodes}:
                            report["cycles_omitted"] += 1
                            continue
                        if row["key"] not in nodes_seen and len(nodes_seen) >= self.max_nodes:
                            report["limits_reached"].append("nodes")
                            continue
                        nodes_seen.add(row["key"])
                        next_nodes = nodes + [{k: row[k] for k in ("key", "entity_id", "name")}]
                        next_edges = edges + [
                            {k: row[k] for k in ("edge_id", "relation", "sources", "source_key", "target_key")}
                        ]
                        evidence = {
                            "nodes": next_nodes,
                            "edges": next_edges,
                            "direction": self.direction,
                            "database": self.database,
                            "source_status": "declared_not_verified",
                        }
                        rendered = json.dumps(evidence, ensure_ascii=False, sort_keys=True)
                        if chars + len(rendered) > self.max_context_chars:
                            report["limits_reached"].append("context_chars")
                            queue.clear()
                            break
                        chars += len(rendered)
                        identity = hashlib.sha256(rendered.encode()).hexdigest()
                        documents.append(
                            Document(id=f"neo4j-path:{identity}", text=rendered, metadata={"evidence_path": evidence})
                        )
                        queue.append((next_nodes, next_edges))
                        if len(documents) >= limit:
                            report["limits_reached"].append("paths")
                            break
                report["nodes_seen"] = len(nodes_seen)
        report["limits_reached"] = sorted(set(report["limits_reached"]))
        report["paths_returned"] = len(documents)
        if report["limits_reached"]:
            report["status"] = "bounded_partial"
        # Each result exposes partial status even through Knowledge.query_knowledge.
        for doc in documents:
            doc.metadata["path_report"] = dict(report)
        return documents, report
