import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from agentuniverse.llm.default.huggingface_hub_llm import HuggingFaceHubLLM
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


def _make_choice(text="Hello"):
    choice = MagicMock()
    choice.message.content = text
    return choice


def _make_response(text="Hello"):
    resp = MagicMock()
    resp.choices = [_make_choice(text)]
    return resp


def _make_stream_chunk(text="Hi"):
    chunk = MagicMock()
    delta = MagicMock()
    delta.content = text
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta = delta
    return chunk


class TestHuggingFaceHubLLM(unittest.TestCase):

    def setUp(self):
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer

        self.llm = HuggingFaceHubLLM(
            model_name="meta-llama/Llama-3.2-3B-Instruct",
            api_key="test-token",
        )
        self.llm.client = None
        self.llm.async_client = None

    def test_call_non_streaming(self):
        """Test synchronous non-streaming call."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = _make_response("Hello world")
        self.llm.client = mock_client

        messages = [{"role": "user", "content": "hi"}]
        output = self.llm.call(messages=messages, streaming=False)
        self.assertEqual(output.text, "Hello world")
        mock_client.chat_completion.assert_called_once()

    def test_call_streaming(self):
        """Test synchronous streaming call."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = iter([
            _make_stream_chunk("Hello "),
            _make_stream_chunk("world"),
        ])
        self.llm.client = mock_client

        messages = [{"role": "user", "content": "hi"}]
        chunks = list(self.llm.call(messages=messages, streaming=True))
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].text, "Hello ")
        self.assertEqual(chunks[1].text, "world")

    def test_acall_non_streaming(self):
        """Test asynchronous non-streaming call."""
        mock_client = AsyncMock()
        mock_client.chat_completion.return_value = _make_response("Async hello")
        self.llm.async_client = mock_client

        messages = [{"role": "user", "content": "hi"}]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        self.assertEqual(output.text, "Async hello")

    def test_acall_streaming(self):
        """Test asynchronous streaming call."""

        async def _async_iter():
            yield _make_stream_chunk("A1")
            yield _make_stream_chunk("A2")

        mock_client = AsyncMock()

        async def _chat_completion(**kwargs):
            if kwargs.get("stream"):
                return _async_iter()
            return _make_response("fallback")

        mock_client.chat_completion = _chat_completion
        self.llm.async_client = mock_client

        messages = [{"role": "user", "content": "hi"}]

        async def _run():
            gen = await self.llm.acall(messages=messages, streaming=True)
            chunks = []
            async for c in gen:
                chunks.append(c)
            return chunks

        chunks = asyncio.run(_run())
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].text, "A1")
        self.assertEqual(chunks[1].text, "A2")

    def test_client_caching(self):
        """Test that _new_client caches the client."""
        with patch("huggingface_hub.InferenceClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = self.llm._new_client()
            c2 = self.llm._new_client()
            self.assertIs(c1, c2)
            mock_cls.assert_called_once()

    def test_async_client_caching(self):
        """Test that _new_async_client caches the async client."""
        with patch("huggingface_hub.AsyncInferenceClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = self.llm._new_async_client()
            c2 = self.llm._new_async_client()
            self.assertIs(c1, c2)
            mock_cls.assert_called_once()

    def test_async_client_is_not_sync_client(self):
        """Test that _new_async_client creates AsyncInferenceClient, not reuses sync."""
        self.llm.client = MagicMock()
        self.llm.async_client = None
        with patch("huggingface_hub.AsyncInferenceClient") as mock_async_cls:
            mock_async_cls.return_value = MagicMock(name="async_client")
            c = self.llm._new_async_client()
            mock_async_cls.assert_called_once()
            self.assertIsNotNone(self.llm.async_client)
            self.assertIsNot(self.llm.async_client, self.llm.client)

    def test_max_context_length_known(self):
        llm = HuggingFaceHubLLM(model_name="meta-llama/Llama-3.2-3B-Instruct")
        self.assertEqual(llm.max_context_length(), 128072)

    def test_max_context_length_unknown(self):
        llm = HuggingFaceHubLLM(model_name="unknown/model")
        self.assertEqual(llm.max_context_length(), 4096)

    def test_build_kwargs_with_api_base(self):
        llm = HuggingFaceHubLLM(
            model_name="test/model",
            api_key="tok",
            api_base="https://custom.endpoint.com",
        )
        kwargs = llm._build_kwargs()
        self.assertEqual(kwargs["url"], "https://custom.endpoint.com")
        self.assertNotIn("model", kwargs)

    def test_build_kwargs_without_api_base(self):
        llm = HuggingFaceHubLLM(model_name="test/model", api_key="tok")
        kwargs = llm._build_kwargs()
        self.assertEqual(kwargs["model"], "test/model")
        self.assertNotIn("url", kwargs)

    def test_get_num_tokens(self):
        text = "Hello, this is a test string."
        token_count = self.llm.get_num_tokens(text)
        self.assertGreater(token_count, 0)


if __name__ == "__main__":
    unittest.main()
