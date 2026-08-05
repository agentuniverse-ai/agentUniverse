import asyncio
import os
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.litellm import LiteLLM

FOUNDRY_KEY = os.environ.get("ANTHROPIC_FOUNDRY_API_KEY", "")
FOUNDRY_BASE = "https://amanrai-test-resource.services.ai.azure.com/anthropic"

requires_key = unittest.skipUnless(FOUNDRY_KEY, "ANTHROPIC_FOUNDRY_API_KEY not set")


@requires_key
class TestLiteLLMCompletion(unittest.TestCase):

    def setUp(self):
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer
        self.llm = LiteLLM(
            model_name="anthropic/claude-sonnet-4-6",
            api_key=FOUNDRY_KEY,
            api_base=FOUNDRY_BASE,
        )

    def test_call_non_streaming(self):
        messages = [{"role": "user", "content": "What is 2+2? Reply with just the number."}]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertIsNotNone(output.text)
        self.assertIn("4", output.text)
        self.assertIsNotNone(output.raw)

    def test_call_streaming(self):
        messages = [{"role": "user", "content": "Say OK and nothing else."}]
        stream = self.llm.call(messages=messages, streaming=True)
        full_text = ""
        for chunk in stream:
            self.assertIsNotNone(chunk.text)
            full_text += chunk.text
        self.assertTrue(len(full_text) > 0)

    def test_acall_non_streaming(self):
        messages = [{"role": "user", "content": "What is 2+2? Reply with just the number."}]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        self.assertIsNotNone(output.text)
        self.assertIn("4", output.text)

    def test_unicode_prompt(self):
        messages = [{"role": "user", "content": "用中文回答：2加2等于几？只回答数字。"}]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertIsNotNone(output.text)

    def test_long_prompt(self):
        messages = [{"role": "user", "content": "Tell me about AI. " * 50 + " Summarize in one sentence."}]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertIsNotNone(output.text)
        self.assertTrue(len(output.text) > 0)

    def test_system_message(self):
        messages = [
            {"role": "system", "content": "You always reply with exactly one word."},
            {"role": "user", "content": "What color is the sky?"},
        ]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertIsNotNone(output.text)

    def test_multi_turn_conversation(self):
        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Hello Alice!"},
            {"role": "user", "content": "What is my name? Reply with just the name."},
        ]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertIsNotNone(output.text)
        self.assertIn("Alice", output.text)

    def test_temperature_override(self):
        messages = [{"role": "user", "content": "Say OK."}]
        output = self.llm.call(messages=messages, streaming=False, temperature=0.0)
        self.assertIsNotNone(output.text)

    def test_max_tokens_override(self):
        messages = [{"role": "user", "content": "Write a very long essay about the universe."}]
        output = self.llm.call(messages=messages, streaming=False, max_tokens=10)
        self.assertIsNotNone(output.text)
        self.assertTrue(len(output.text) < 200)

    def test_get_num_tokens(self):
        count = self.llm.get_num_tokens("Hello world, this is a test.")
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)


@requires_key
class TestLiteLLMEdgeCases(unittest.TestCase):

    def setUp(self):
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer

    def test_nonexistent_model(self):
        llm = LiteLLM(
            model_name="anthropic/nonexistent-model-xyz",
            api_key=FOUNDRY_KEY,
            api_base=FOUNDRY_BASE,
        )
        with self.assertRaises(Exception):
            llm.call(messages=[{"role": "user", "content": "test"}], streaming=False)

    def test_env_var_fallback(self):
        os.environ["ANTHROPIC_API_KEY"] = FOUNDRY_KEY
        os.environ["ANTHROPIC_API_BASE"] = FOUNDRY_BASE
        try:
            llm = LiteLLM(model_name="anthropic/claude-sonnet-4-6")
            # This may fail due to env var routing differences — the test
            # verifies the code path doesn't crash on initialization
            self.assertIsNotNone(llm)
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_BASE", None)


class TestLiteLLMMocked(unittest.TestCase):
    """Deterministic tests with a stubbed litellm module (no keys or network)."""

    def setUp(self):
        ApplicationConfigManager().app_configer = AppConfiger()
        self._orig_litellm = sys.modules.get("litellm")
        self._fake = types.ModuleType("litellm")
        sys.modules["litellm"] = self._fake
        self.llm = LiteLLM(model_name="openai/gpt-4o", api_key="sk-test")

    def tearDown(self):
        if self._orig_litellm is not None:
            sys.modules["litellm"] = self._orig_litellm
        else:
            sys.modules.pop("litellm", None)

    @staticmethod
    def _response(text):
        choice = SimpleNamespace(message=SimpleNamespace(content=text))
        resp = SimpleNamespace(choices=[choice])
        resp.model_dump = lambda: {"choices": [{"message": {"content": text}}]}
        return resp

    @staticmethod
    def _chunk(text):
        choice = SimpleNamespace(delta=SimpleNamespace(content=text))
        chunk = SimpleNamespace(choices=[choice])
        chunk.model_dump = lambda: {"choices": [{"delta": {"content": text}}]}
        return chunk

    def test_call_non_streaming(self):
        self._fake.completion = lambda **kwargs: self._response("4")
        output = self.llm.call(
            messages=[{"role": "user", "content": "2+2?"}], streaming=False
        )
        self.assertEqual(output.text, "4")
        self.assertIn("choices", output.raw)

    def test_call_streaming(self):
        self._fake.completion = lambda **kwargs: iter(
            [self._chunk("O"), self._chunk("K")]
        )
        chunks = list(
            self.llm.call(messages=[{"role": "user", "content": "hi"}], streaming=True)
        )
        self.assertEqual("".join(c.text for c in chunks), "OK")

    def test_acall_non_streaming(self):
        async def _acompletion(**kwargs):
            return self._response("4")

        self._fake.acompletion = _acompletion
        output = asyncio.run(
            self.llm.acall(
                messages=[{"role": "user", "content": "2+2?"}], streaming=False
            )
        )
        self.assertEqual(output.text, "4")

    def test_acall_streaming(self):
        async def _agen():
            for token in ["O", "K"]:
                yield self._chunk(token)

        async def _acompletion(**kwargs):
            return _agen()

        self._fake.acompletion = _acompletion

        async def _run():
            stream = await self.llm.acall(
                messages=[{"role": "user", "content": "hi"}], streaming=True
            )
            return [c async for c in stream]

        chunks = asyncio.run(_run())
        self.assertEqual("".join(c.text for c in chunks), "OK")

    def test_as_langchain_adapter(self):
        from langchain_core.language_models.base import BaseLanguageModel

        langchain_llm = self.llm.as_langchain()
        self.assertIsInstance(langchain_llm, BaseLanguageModel)
        self.assertIs(langchain_llm.llm, self.llm)


if __name__ == "__main__":
    unittest.main()
