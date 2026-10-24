#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.memory.message import Message


class TestMessageSerialization(unittest.TestCase):
    def test_to_dict_preserves_id_for_round_trip(self):
        message = Message(
            id="message-1",
            type="human",
            content="hello",
            source="user",
        )

        restored = Message.from_dict(message.to_dict())

        self.assertEqual(restored.id, "message-1")
        self.assertEqual(restored.type, message.type)
        self.assertEqual(restored.content, message.content)
        self.assertEqual(restored.source, message.source)


if __name__ == "__main__":
    unittest.main()
