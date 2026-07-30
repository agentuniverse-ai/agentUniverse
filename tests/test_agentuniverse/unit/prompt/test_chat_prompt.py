#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt


class TestChatPrompt(unittest.TestCase):
    def test_extract_placeholders_supports_multimodal_content(self):
        prompt = ChatPrompt(messages=[
            Message(
                type=ChatMessageEnum.HUMAN.value,
                content="Hello {name}",
            ),
            Message(
                type=ChatMessageEnum.HUMAN.value,
                content=[
                    {"type": "text", "text": "Describe {topic}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/image.png"},
                    },
                ],
            ),
        ])

        self.assertEqual(
            prompt.extract_placeholders(),
            ["name", "topic"],
        )


if __name__ == "__main__":
    unittest.main()
