#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, Generation

from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser


class TestReasoningOutputParser(unittest.TestCase):
    def test_plain_generation_without_message_is_supported(self):
        result = ReasoningOutputParser().parse_result(
            [Generation(text="answer")]
        )

        self.assertEqual(result, {"text": "answer"})

    def test_chat_generation_keeps_reasoning_content(self):
        result = ReasoningOutputParser().parse_result([
            ChatGeneration(
                message=AIMessage(
                    content="answer",
                    additional_kwargs={"reasoning_content": "analysis"},
                )
            )
        ])

        self.assertEqual(
            result,
            {"text": "answer", "reasoning_content": "analysis"},
        )


if __name__ == "__main__":
    unittest.main()
