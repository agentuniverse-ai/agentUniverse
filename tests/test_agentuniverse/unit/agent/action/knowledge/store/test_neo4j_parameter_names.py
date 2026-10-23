"""Cypher parameter names must not bind Python Session.run arguments."""
from types import SimpleNamespace

import pytest

pytest.importorskip('neo4j')
pytest.importorskip('pandas')

from neo4j import GraphDatabase, Record, Session
from neo4j._sync.work import session as session_module

from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def store(monkeypatch):
    sent = []

    class Result:
        def __init__(self, *args):
            pass

        def _run(self, query, parameters, *args):
            sent.append((query, parameters))
            self.parameters = parameters

        def __iter__(self):
            return iter([Record([('bound', self.parameters)])])

        def consume(self):
            pass

    def connect(self, *args):
        self._connection = SimpleNamespace(telemetry=lambda *args: None,
                                          send_all=lambda: None, fetch_all=lambda: None)

    monkeypatch.setattr(Session, '_connect', connect)
    monkeypatch.setattr(Session, '_disconnect', lambda self, *args, **kwargs: setattr(self, '_connection', None))
    monkeypatch.setattr(session_module, 'Result', Result)
    # Real Driver and Session: retain native run signature, argument binding,
    # parameter-map construction and session lifecycle. No Bolt connection.
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'test'))
    store = Neo4jStore(driver=driver)
    yield store, sent
    driver.close()


@pytest.mark.parametrize('parameters', [
    {'query': 'search term'},
    {'parameters': 'parameter value'},
    {'parameters': {'nested': 'must stay nested'}},
    {'query': 'search term', 'parameters': 42, 'ordinary': 'value'},
    {'ordinary': 'value'},
    {},
])
@pytest.mark.parametrize('entrypoint', ['execute', 'query'])
def test_public_query_preserves_parameter_names(store, parameters, entrypoint):
    store, sent = store
    cypher = 'RETURN ' + (', '.join(f'${key} AS value_{i}' for i, key in enumerate(parameters)) or '1 AS value')
    if entrypoint == 'execute':
        records = store.execute_cypher(cypher, parameters)
    else:
        document = store.query(Query(query_str=cypher, ext_info={
            'query_type': 'direct_cypher', 'query_params': parameters}))[0]
        records = document.graph_data
    assert sent == [(cypher, parameters)]
    assert records.iloc[0]['bound'] == parameters
