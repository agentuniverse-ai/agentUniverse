from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore


class _FakeSession:
    def __init__(self):
        self.calls = []
        self.closed = False

    def run(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return []

    def close(self):
        self.closed = True


def test_cypher_parameter_names_are_kept_inside_parameter_map():
    session = _FakeSession()
    params = {"query": "term", "parameters": {"nested": "value"}}

    Neo4jStore._execute_cypher(
        session,
        "RETURN $query AS value, $parameters AS metadata",
        params,
    )

    assert session.calls == [
        (
            ("RETURN $query AS value, $parameters AS metadata",),
            {"parameters": params},
        )
    ]
    assert session.closed is True
