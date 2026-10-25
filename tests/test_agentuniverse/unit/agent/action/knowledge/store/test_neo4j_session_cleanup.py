import pytest

from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore


class FailingResult:
    def __iter__(self):
        raise RuntimeError("result stream failed")


class Session:
    def __init__(self):
        self.closed = False

    def run(self, query, **params):
        return FailingResult()

    def close(self):
        self.closed = True


def test_neo4j_session_closes_when_result_iteration_fails():
    session = Session()

    with pytest.raises(RuntimeError, match="result stream failed"):
        Neo4jStore._execute_cypher(session, "RETURN 1")

    assert session.closed is True
