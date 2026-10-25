"""Store instances must not inherit another component's Milvus connection."""
import importlib
from copy import deepcopy

import pytest

pytest.importorskip('pymilvus')
from pymilvus import connections

from agentuniverse.agent.action.knowledge.store.milvus_store import MilvusStore


@pytest.fixture
def native_registry(monkeypatch):
    module = importlib.import_module('pymilvus.orm.connections')
    store_module = importlib.import_module('agentuniverse.agent.action.knowledge.store.milvus_store')
    original_aliases = {alias for alias, _ in connections.list_connections()}
    created = []
    probes = []

    class OfflineGrpcHandler:
        def __init__(self, **kwargs):
            self.options = deepcopy(kwargs)
            created.append(self)

        def _wait_for_channel_ready(self, timeout):
            pass

        def close(self):
            pass

    def has_collection(name, using):
        probes.append((name, using))
        return False

    # Keep native Connections.connect/has_connection/registry behavior; replace
    # only the RPC transport and the collection-existence network operation.
    monkeypatch.setattr(module, 'GrpcHandler', OfflineGrpcHandler)
    monkeypatch.setattr(store_module.utility, 'has_collection', has_collection)
    try:
        yield created, probes
    finally:
        for alias, _ in connections.list_connections():
            if alias not in original_aliases:
                connections.remove_connection(alias)


def options(**overrides):
    return {'host': 'unit-au-milvus', 'port': '19530', 'db_name': 'shared',
            'user': 'alice', 'password': 'offline-first', **overrides}


@pytest.mark.parametrize('overrides', [
    {'user': 'bob', 'password': 'offline-second'},
    {'password': 'offline-second'},
    {'token': 'offline-token'},
    {'secure': True},
    {},
])
def test_separate_stores_keep_their_connection_options(native_registry, overrides):
    created, probes = native_registry
    first = MilvusStore(connection_args=options())
    second_options = options(**overrides)
    second = MilvusStore(connection_args=second_options)
    first._new_client()
    second._new_client()
    assert first.connection_name != second.connection_name
    assert len(created) == 2
    assert created[1].options['user'] == second_options['user']
    assert created[1].options['password'] == second_options['password']
    assert created[1].options.get('token', '') == second_options.get('token', '')
    assert created[1].options.get('secure', False) == second_options.get('secure', False)
    assert probes == [('milvus_db', first.connection_name), ('milvus_db', second.connection_name)]
    assert connections.has_connection(first.connection_name)
    assert connections.has_connection(second.connection_name)
    assert 'offline-first' not in first.connection_name
    assert 'offline-second' not in second.connection_name
    assert 'offline-token' not in second.connection_name


def test_repeated_client_initialization_reuses_own_connection(native_registry):
    created, _ = native_registry
    store = MilvusStore(connection_args=options())
    store._new_client()
    alias = store.connection_name
    store._new_client()
    assert store.connection_name == alias
    assert len(created) == 1


def test_existing_external_alias_cannot_supply_store_credentials(native_registry):
    created, _ = native_registry
    external_alias = 'unit-au-milvus_19530_shared'
    connections.connect(alias=external_alias, **options(user='external', password='offline-external'))
    store = MilvusStore(connection_args=options())
    store._new_client()
    assert store.connection_name != external_alias
    assert len(created) == 2
    assert created[1].options['user'] == 'alice'
    assert connections.get_connection_addr(external_alias)['user'] == 'external'
