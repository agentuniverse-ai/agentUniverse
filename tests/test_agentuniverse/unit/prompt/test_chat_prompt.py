#!/usr/bin/env python3

import unittest

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt


def test_generate_image_prompt_uses_standard_jpeg_mime_type(tmp_path):
    image_path = tmp_path / "photo.jpg"
    image_path.write_bytes(b"jpeg data")
    prompt = ChatPrompt()

    prompt.generate_image_prompt([str(image_path)])

    image_url = prompt.messages[-1].content[0]["image_url"]["url"]
    assert image_url.startswith("data:image/jpeg;base64,")


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
