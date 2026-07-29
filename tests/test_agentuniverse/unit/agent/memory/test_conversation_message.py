#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.memory.conversation_memory.conversation_message import (
    ConversationMessage,
)


class TestConversationMessage(unittest.TestCase):
    def test_default_ids_are_unique_per_message(self):
        first = ConversationMessage()
        second = ConversationMessage()

        self.assertIsNotNone(first.id)
        self.assertIsNotNone(second.id)
        self.assertNotEqual(first.id, second.id)


if __name__ == "__main__":
    unittest.main()
