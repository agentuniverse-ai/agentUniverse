# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/13 00:00
# @Author  : Yue Wang
# @FileName: test_prompt_util.py

import unittest

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt

from examples.sample_apps.basic_sop_app.intelligence.utils.product.prompt_util import (
    convert_prompt_to_message,
    get_prompt_str,
)


class TestPromptUtil(unittest.TestCase):
    """Unit tests for the prompt_util conversion helpers."""

    def setUp(self):
        """Build a ChatPrompt fixture mixing system/human messages."""
        self.prompt = ChatPrompt(messages=[
            Message(type=ChatMessageEnum.SYSTEM.value, content='You are a product assistant.'),
            Message(type=ChatMessageEnum.HUMAN.value, content='Recommend {product} for {customer}.'),
        ])
        self.agent_input = {'product': 'medical insurance', 'customer': 'Alice'}

    def test_convert_returns_list_of_role_content_dicts(self):
        """convert_prompt_to_message returns one dict per message."""
        result = convert_prompt_to_message(self.agent_input, self.prompt)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertIn('role', item)
            self.assertIn('content', item)

    def test_convert_system_message_maps_to_system_role(self):
        """System messages keep raw content and map to role 'system'."""
        result = convert_prompt_to_message(self.agent_input, self.prompt)
        self.assertEqual(result[0]['role'], 'system')
        self.assertEqual(result[0]['content'], 'You are a product assistant.')

    def test_convert_human_message_is_formatted_with_agent_input(self):
        """Human messages are str-formatted with agent_input and map to role 'user'."""
        result = convert_prompt_to_message(self.agent_input, self.prompt)
        self.assertEqual(result[1]['role'], 'user')
        self.assertEqual(result[1]['content'],
                         'Recommend medical insurance for Alice.')

    def test_convert_supports_user_type_message(self):
        """Messages typed 'user' are treated the same as 'human'."""
        prompt = ChatPrompt(messages=[Message(type=ChatMessageEnum.USER.value, content='Hi {name}')])
        result = convert_prompt_to_message({'name': 'Bob'}, prompt)
        self.assertEqual(result, [{'role': 'user', 'content': 'Hi Bob'}])

    def test_convert_skips_non_system_non_human_messages(self):
        """AI messages without formatting are not emitted by the converter."""
        prompt = ChatPrompt(messages=[Message(type=ChatMessageEnum.AI.value, content='ok')])
        self.assertEqual(convert_prompt_to_message(self.agent_input, prompt), [])

    def test_get_prompt_str_contains_system_prompt_prefix(self):
        """get_prompt_str renders a System prompt line with the raw content."""
        prompt_str = get_prompt_str(self.agent_input, self.prompt)
        self.assertIn('System prompt: You are a product assistant.', prompt_str)

    def test_get_prompt_str_formats_user_content(self):
        """get_prompt_str renders formatted user content under a User prompt line."""
        prompt_str = get_prompt_str(self.agent_input, self.prompt)
        self.assertIn('User prompt: Recommend medical insurance for Alice.', prompt_str)
        self.assertTrue(prompt_str.endswith('\n\n'))

    def test_get_prompt_str_preserves_message_order(self):
        """System output always precedes user output in the string."""
        prompt_str = get_prompt_str(self.agent_input, self.prompt)
        self.assertLess(prompt_str.index('System prompt:'),
                        prompt_str.index('User prompt:'))


if __name__ == '__main__':
    unittest.main()
