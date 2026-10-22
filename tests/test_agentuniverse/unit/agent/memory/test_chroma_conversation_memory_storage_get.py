# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for ``ChromaConversationMemoryStorage.get``.

``memory_types`` is an optional retrieval parameter: ``Agent.get_memory_params``
only puts it into the memory parameters when the agent's memory component
declares it, so ``get()`` has to work without it, exactly like the sqlite and
elasticsearch conversation storages do.
"""

import unittest
from unittest.mock import MagicMock

from agentuniverse.agent.memory.conversation_memory.enum import (
    ConversationMessageSourceType,
)
from agentuniverse.agent.memory.conversation_memory.memory_storage.chroma_conversation_memory_storage import (
    ChromaConversationMemoryStorage,
)

EMPTY_RESULT = {'ids': [], 'metadatas': [], 'documents': []}


class ChromaConversationMemoryGetTest(unittest.TestCase):
    """``get()`` must tolerate a missing ``memory_types`` parameter."""

    def setUp(self):
        # The collection is stubbed so the test needs neither a Chroma server
        # nor the default embedding model; get() is exercised as-is.
        self.storage = ChromaConversationMemoryStorage(name='chroma_memory_storage')
        self.storage._collection = MagicMock()
        self.storage._collection.get.return_value = dict(EMPTY_RESULT)

    def test_get_without_memory_types_does_not_raise(self):
        """The parameters Agent.get_memory_params builds must be accepted."""
        messages = self.storage.get(session_id='session', agent_id='agent_a', top_k=20)

        self.assertEqual(messages, [])
        self.storage._collection.get.assert_called_once()

    def test_get_without_memory_types_filters_by_agent_only(self):
        self.storage.get(session_id='session', agent_id='agent_a', top_k=20)

        where = self.storage._collection.get.call_args.kwargs['where']
        self.assertIn({'session_id': 'session'}, where['$and'])
        agent_condition = where['$and'][1]
        self.assertEqual(agent_condition, {
            '$and': [
                {'target': 'agent_a'},
                {'target_type': ConversationMessageSourceType.AGENT.value},
            ]
        })

    def test_get_with_memory_types_keeps_the_configured_source_branch(self):
        self.storage.get(session_id='session', agent_id='agent_a', top_k=20,
                         memory_types=['agent', 'tool'])

        where = self.storage._collection.get.call_args.kwargs['where']
        agent_condition = where['$and'][1]
        self.assertIn('$or', agent_condition)
        self.assertEqual(agent_condition['$or'][1], {
            '$and': [
                {'source': 'agent_a'},
                {'source_type': ConversationMessageSourceType.AGENT.value},
                {'target_type': {'$in': ['agent', 'tool']}},
            ]
        })

    def test_get_with_empty_memory_types_falls_back_to_target_only(self):
        self.storage.get(session_id='session', agent_id='agent_a', top_k=20,
                         memory_types=[])

        where = self.storage._collection.get.call_args.kwargs['where']
        self.assertNotIn('$or', where['$and'][1])

    def test_get_with_trace_id_and_memory_types(self):
        self.storage.get(session_id='session', agent_id='agent_a', top_k=20,
                         trace_id='trace-1', memory_types=['agent'])

        where = self.storage._collection.get.call_args.kwargs['where']
        self.assertIn({'trace_id': 'trace-1'}, where['$and'])


if __name__ == '__main__':
    unittest.main()
