# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:10
# @Author  : yuewang
# @FileName: test_es_conversation_memory_storage.py
"""Unit tests for ElasticsearchMemoryStorage and DefaultMemoryConverter."""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.memory_storage.es_conversation_memory_storage import (
    DefaultMemoryConverter,
    ElasticsearchMemoryStorage,
)


def _hit(_id, session_id, content, ts):
    return {
        '_id': _id,
        '_source': {
            'session_id': session_id, 'source': 'agent_a', 'source_type': 'agent',
            'target': 'agent_b', 'target_type': 'agent', 'content': content,
            'prefix': None, 'timestamp': ts, 'params': '{}', 'pair_id': None,
            'type': 'output', 'trace_id': 'trace-1', 'additional_args': None,
        },
    }


class TestDefaultMemoryConverter:
    """Test the ES bulk-action and hit conversions."""

    @pytest.fixture
    def converter(self):
        return DefaultMemoryConverter('memory_index')

    def test_to_es_action_format(self, converter):
        msg = ConversationMessage(
            id='doc-1', content='hello', type='output', source='a', target='b',
            metadata={'timestamp': datetime(2025, 1, 2, 3, 4, 5)})
        action = converter.to_es_action(msg, session_id='s1')
        lines = action.split('\n')
        assert len(lines) == 2
        index_info = json.loads(lines[0])
        assert index_info == {'index': {'_index': 'memory_index', '_id': 'doc-1'}}
        doc = json.loads(lines[1])
        assert doc['session_id'] == 's1'
        assert doc['content'] == 'hello'
        assert doc['timestamp'] == '2025-01-02T03:04:05'

    def test_from_es_hit(self, converter):
        msg = converter.from_es_hit(_hit('h1', 'sess-9', 'world', '2025-06-01T10:00:00'))
        assert isinstance(msg, ConversationMessage)
        assert msg.id == 'h1'
        assert msg.conversation_id == 'sess-9'
        assert msg.content == 'world'
        assert msg.metadata['timestamp'] == datetime(2025, 6, 1, 10, 0, 0)
        assert msg.metadata['gmt_created'] == '2025-06-01T10:00:00'

    def test_round_trip(self, converter):
        msg = ConversationMessage(id='r1', content='rt', type='input',
                                  metadata={'timestamp': datetime(2025, 3, 3)})
        doc = json.loads(converter.to_es_action(msg, session_id='s').split('\n')[1])
        restored = converter.from_es_hit({'_id': 'r1', '_source': doc})
        assert restored.content == 'rt'
        assert restored.type == 'input'
        assert restored.conversation_id == 's'


class TestElasticsearchMemoryStorageQueries:
    """Test query construction with a mocked httpx client."""

    @pytest.fixture
    def storage(self):
        client = MagicMock()
        client.post.return_value = MagicMock(status_code=200,
                                             json=lambda: {'hits': {'hits': []}})
        # model_construct skips type validation so the mock client is accepted
        return ElasticsearchMemoryStorage.model_construct(
            client=client, memory_converter=DefaultMemoryConverter('idx'))

    def test_get_builds_session_query_and_reverses(self, storage):
        storage.client.post.return_value = MagicMock(
            status_code=200, json=lambda: {
                'hits': {'hits': [
                    _hit('h2', 's1', 'newer', '2025-01-02T00:00:00'),
                    _hit('h1', 's1', 'older', '2025-01-01T00:00:00'),
                ]}})
        result = storage.get(session_id='s1')
        sent_query = storage.client.post.call_args.kwargs['json']
        assert {'term': {'session_id': 's1'}} in sent_query['query']['bool']['must']
        assert [m.content for m in result] == ['older', 'newer']

    def test_delete_includes_trace_clause(self, storage):
        storage.delete(session_id='s1', trace_id='t9')
        url = storage.client.post.call_args.args[0]
        assert url.endswith('/memory/_delete_by_query')
        must = storage.client.post.call_args.kwargs['json']['query']['bool']['must']
        assert {'term': {'session_id': 's1'}} in must
        assert {'term': {'trace_id': 't9'}} in must


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
