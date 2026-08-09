#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for LLM channel choices[0] / streaming chunk KeyError / delta None guards."""

import unittest


class TestLLMChannelNonStreamingChoicesGuard(unittest.TestCase):

    def test_call_source_guards_empty_choices(self):
        import inspect
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
        src = inspect.getsource(LLMChannel._call)
        self.assertIn("not chat_completion.choices", src,
                      "_call must guard empty choices before indexing [0]")

    def test_acall_source_guards_empty_choices(self):
        import inspect
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
        src = inspect.getsource(LLMChannel._acall)
        self.assertIn("not chat_completion.choices", src,
                      "_acall must guard empty choices before indexing [0]")


class TestLLMChannelStreamingParseResultGuard(unittest.TestCase):

    def test_parse_result_uses_get_for_choices(self):
        import inspect
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
        src = inspect.getsource(LLMChannel.parse_result)
        self.assertIn('chunk.get("choices")', src,
                      "parse_result must use .get('choices') not chunk['choices']")
        self.assertIn('choice.get("delta") or {}', src,
                      "parse_result must guard delta None")

    def test_parse_result_no_subscript_choices(self):
        import inspect
        from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
        src = inspect.getsource(LLMChannel.parse_result)
        # The dangerous subscript form must be gone from code lines.
        code_lines = [l for l in src.split("\n")
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            self.assertNotIn('chunk["choices"]', line,
                             f"parse_result must not subscript choices: {line!r}")


class TestOpenAIStyleLLMGuards(unittest.TestCase):

    def test_call_guards_empty_choices(self):
        import inspect
        from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM
        src = inspect.getsource(OpenAIStyleLLM._call)
        self.assertIn("not chat_completion.choices", src)

    def test_acall_guards_empty_choices(self):
        import inspect
        from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM
        src = inspect.getsource(OpenAIStyleLLM._acall)
        self.assertIn("not chat_completion.choices", src)

    def test_parse_result_uses_get(self):
        import inspect
        from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM
        src = inspect.getsource(OpenAIStyleLLM.parse_result)
        self.assertIn('chunk.get("choices")', src)
        self.assertIn('choice.get("delta") or {}', src)


class TestDefaultChannelLangchainInstanceGuards(unittest.TestCase):

    def test_no_subscript_choices(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for _ in range(10):
            candidate = os.path.join(
                here, "agentuniverse", "llm", "llm_channel",
                "langchain_instance", "default_channel_langchain_instance.py")
            if os.path.exists(candidate):
                filepath = candidate
                break
            here = os.path.dirname(here)
        else:
            self.skipTest("Could not locate file")

        with open(filepath) as f:
            src = f.read()
        code_lines = [l for l in src.split("\n")
                      if l.strip() and not l.strip().startswith("#")]
        for line in code_lines:
            self.assertNotIn(
                'chunk["choices"]', line,
                f"must use .get('choices') not subscript: {line!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
