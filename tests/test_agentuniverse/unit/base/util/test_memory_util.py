#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.util.memory_util import get_memory_string


class TestGetMemoryString(unittest.TestCase):
    def test_plain_input_message_without_trace_fields_is_rendered(self):
        message = Message(
            type="input",
            content="hello",
            metadata={},
        )

        result = get_memory_string([message])

        self.assertIn("hello", result)


if __name__ == "__main__":
    unittest.main()
