"""Actual Neo4j graph traversal, including cycles, parallel edges and provenance."""

import asyncio
import os
import uuid

import pytest
from neo4j import GraphDatabase

from agentuniverse.agent.action.knowledge.store.neo4j_evidence_store import Neo4jEvidenceStore
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def graph():
    driver = GraphDatabase.driver(os.environ["AU_EVIDENCE_NEO4J_URI"], auth=None)
    prefix = "b14-" + uuid.uuid4().hex
    with driver.session() as session:
        session.run(
            """CREATE (a:EvidenceEntity {entity_id:$a,name:'same',test:$p}),
            (b:EvidenceEntity {entity_id:$b,name:'same',test:$p}),
            (c:EvidenceEntity {entity_id:$c,name:'third',test:$p}),
            (d:EvidenceEntity {entity_id:$d,name:'missing-source',test:$p}),
            (a)-[:CITES {source_doc_ids:['doc-A']}]->(b),
            (a)-[:CITES {source_doc_ids:['doc-B']}]->(b),
            (b)-[:CITES {source_doc_ids:['doc-C']}]->(c),
            (c)-[:CITES {source_doc_ids:['doc-cycle']}]->(a),
            (a)-[:CITES]->(d),
            (a)-[:IGNORED {source_doc_ids:['doc-ignore']}]->(c)""",
            a=prefix + "a",
            b=prefix + "b",
            c=prefix + "c",
            d=prefix + "d",
            p=prefix,
        ).consume()
    try:
        yield driver, prefix
    finally:
        with driver.session() as session:
            session.run("MATCH (n:EvidenceEntity {test:$p}) DETACH DELETE n", p=prefix).consume()
        driver.close()


def store(graph, **kwargs):
    return Neo4jEvidenceStore(client=graph[0], relationship_types=["CITES"], **kwargs)


def query(graph):
    return Query(ext_info={"entity_id": graph[1] + "a"})


def test_paths_parallel_edges_cycles_and_sources(graph):
    docs, report = store(graph, max_hops=4).query_with_report(query(graph))
    assert len(docs) == 4
    assert report["cycles_omitted"] == 2
    assert report["missing_sources"] == 1
    assert report["status"] == "complete_within_hops"
    assert len({d.id for d in docs}) == 4
    for doc in docs:
        path = doc.metadata["evidence_path"]
        assert len(path["nodes"]) == len(path["edges"]) + 1
        assert len({n["key"] for n in path["nodes"]}) == len(path["nodes"])
        assert all(edge["sources"] for edge in path["edges"])
        assert all(edge["relation"] == "CITES" for edge in path["edges"])
        assert path["source_status"] == "declared_not_verified"
        assert doc.metadata["path_report"] == report
    assert {tuple(d.metadata["evidence_path"]["edges"][0]["sources"]) for d in docs} == {("doc-A",), ("doc-B",)}
    assert (
        docs[0].metadata["evidence_path"]["nodes"][0]["name"] == docs[0].metadata["evidence_path"]["nodes"][1]["name"]
    )


@pytest.mark.parametrize("direction,count", [("outgoing", 2), ("incoming", 1), ("both", 3)])
def test_direction_and_hops(graph, direction, count):
    docs = store(graph, direction=direction, max_hops=1).query(query(graph))
    assert len(docs) == count
    assert all(len(d.metadata["evidence_path"]["edges"]) == 1 for d in docs)
    for doc in docs:
        path = doc.metadata["evidence_path"]
        edge = path["edges"][0]
        if direction == "incoming":
            assert edge["target_key"] == path["nodes"][0]["key"]


@pytest.mark.parametrize(
    "options,reason",
    [
        ({"max_edges": 1}, "edges"),
        ({"max_nodes": 1}, "nodes"),
        ({"max_paths": 1}, "paths"),
        ({"max_context_chars": 1}, "context_chars"),
    ],
)
def test_budgets_and_truthful_partial_reports(graph, options, reason):
    docs, report = store(graph, **options).query_with_report(query(graph))
    assert reason in report["limits_reached"]
    assert report["status"] == "bounded_partial"
    assert report["rows_retained"] <= options.get("max_edges", 100)
    assert report["nodes_seen"] <= options.get("max_nodes", 50)
    assert report["paths_returned"] == len(docs)


def test_identity_missing_ambiguous_and_bound_parameters(graph):
    s = store(graph)
    docs, report = s.query_with_report(Query(ext_info={"entity_id": "x'}) DETACH DELETE n //"}))
    assert docs == [] and report["status"] == "root_not_found"
    with graph[0].session() as session:
        assert session.run("MATCH (n:EvidenceEntity {test:$p}) RETURN count(n) AS c", p=graph[1]).single()["c"] == 4
        session.run("CREATE (:EvidenceEntity {entity_id:$id,test:$p})", id=graph[1] + "a", p=graph[1]).consume()
    with pytest.raises(ValueError, match="Ambiguous"):
        s.query(query(graph))
    with pytest.raises(ValueError, match="entity_id"):
        s.query(Query(query_str="same"))
    with pytest.raises(NotImplementedError):
        s.insert_document([])


def test_async_and_type_allowlist(graph):
    s = store(graph)
    assert [d.id for d in asyncio.run(s.async_query(query(graph)))] == [d.id for d in s.query(query(graph))]
    s.relationship_types = ["CITES`) DELETE n //"]
    assert s.query(query(graph)) == []


def test_knowledge_returns_path_provenance(graph):
    from unittest.mock import patch

    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.configer import Configer

    managers = [StoreManager(), RagRouterManager()]
    pools = [dict(m._instance_obj_map) for m in managers]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge = None
    try:
        config = Configer()
        config.value = {"BASE_INFO": {"appname": "paths-test"}}
        apps.app_configer = AppConfiger().load_by_configer(config)
        s = store(graph, max_paths=1)
        s.name = "evidence_paths"
        router = BaseRouter(name="base_router")
        for m, c in zip(managers, [s, router]):
            m.register(c.get_instance_code(), c)
        knowledge = Knowledge(stores=["evidence_paths"])
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            docs = knowledge.query_knowledge(ext_info={"entity_id": graph[1] + "a"})
        assert len(docs) == 1
        assert docs[0].metadata["evidence_path"]["edges"][0]["sources"]
        assert docs[0].metadata["path_report"]["status"] == "bounded_partial"
    finally:
        if knowledge:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        for m, pool in zip(managers, pools):
            m._instance_obj_map.clear()
            m._instance_obj_map.update(pool)
        apps.app_configer = previous


@pytest.mark.parametrize("sources", [[], [""], "single-string"])
def test_invalid_source_declarations_are_omitted(graph, sources):
    with graph[0].session() as session:
        session.run(
            "MATCH (n:EvidenceEntity {test:$p})-[r:CITES]->() SET r.source_doc_ids=$sources",
            p=graph[1],
            sources=sources,
        ).consume()
    docs, report = store(graph).query_with_report(query(graph))
    assert docs == []
    assert report["missing_sources"] == 3


def test_database_errors_propagate_and_driver_remains_caller_owned(graph):
    from neo4j.exceptions import ClientError

    with pytest.raises(ClientError):
        store(graph, database="nonexistent_b14_database").query(query(graph))
    assert len(store(graph).query(query(graph))) == 4
