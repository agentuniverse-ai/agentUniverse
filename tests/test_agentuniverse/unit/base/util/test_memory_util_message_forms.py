# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/21
# @FileName: test_memory_util_message_forms.py
import unittest

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import generate_messages, get_memory_string


class TestGetMemoryStringMessageForms(unittest.TestCase):
    """get_memory_string must accept the same message forms as
    generate_messages (str / dict / Message), since callers pass raw
    chat_history lists straight through (AgentTemplate.process_memory)."""

    def test_dict_elements_are_rendered(self):
        result = get_memory_string([{'type': 'human', 'content': 'hi'}], 'agent1')
        self.assertIn('hi', result)

    def test_str_elements_are_rendered(self):
        result = get_memory_string(['hello'], 'agent1')
        self.assertIn('hello', result)

    def test_output_typed_message_without_trace_id_is_rendered(self):
        message = Message(type='output', content='the answer', metadata={})
        result = get_memory_string([message], 'agent1')
        self.assertIn('the answer', result)

    def test_current_trace_messages_are_still_skipped(self):
        from unittest import mock

        from agentuniverse.agent.memory.conversation_memory.conversation_message import \
            ConversationMessage

        message = ConversationMessage(type='output', content='current turn',
                                      metadata={}, trace_id='trace-1')
        with mock.patch(
                'agentuniverse.base.util.memory_util.FrameworkContextManager'
        ) as context_manager_cls:
            context_manager_cls.return_value.get_context.return_value = 'trace-1'
            result = get_memory_string([message], 'agent1')
        self.assertEqual('', result)

    def test_generate_messages_contract_is_unchanged(self):
        messages = generate_messages(['plain', {'type': 'human', 'content': 'hi'}])
        self.assertEqual([Message, Message], [type(m) for m in messages])

    def test_stored_input_typed_message_renders_on_next_turn(self):
        """Two-turn persistence path: Agent.process_memory converts a dict
        chat_history entry into a plain Message and stores it; the next
        turn's load_memory reads it back and must render it."""
        from agentuniverse.agent.memory.memory_storage.ram_memory_storage import \
            RamMemoryStorage

        storage = RamMemoryStorage()
        # turn 1: dict chat_history -> generate_messages -> memory.add
        storage.add(generate_messages([{'type': 'input', 'content': 'q1'}]),
                    session_id='s', agent_id='a')
        # turn 2: memory.get -> get_memory_string (agent_util.load_memory)
        stored = storage.get(session_id='s', agent_id='a')
        self.assertEqual([(Message, 'input')],
                         [(type(m), m.type) for m in stored])
        self.assertFalse(hasattr(stored[0], 'trace_id'))
        result = get_memory_string(stored, 'a')
        self.assertIn('q1', result)


if __name__ == '__main__':
    unittest.main()
