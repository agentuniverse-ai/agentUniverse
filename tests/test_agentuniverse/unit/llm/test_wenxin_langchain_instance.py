import unittest
from types import SimpleNamespace

from langchain_core.messages import HumanMessage

from agentuniverse.llm.wenxin_langchain_instance import WenXinLangChainInstance


USAGE = {"prompt_tokens": 2, "completion_tokens": 1}
RAW_CHUNK = {"result": "hi", "usage": USAGE, "body": {"id": "request-id"}}


class FakeWenXinLLM:
    def call(self, **kwargs):
        return iter([SimpleNamespace(raw=RAW_CHUNK)])

    async def acall(self, **kwargs):
        async def chunks():
            yield SimpleNamespace(raw=RAW_CHUNK)

        return chunks()


def build_instance():
    instance = object.__new__(WenXinLangChainInstance)
    object.__setattr__(instance, "llm", FakeWenXinLLM())
    object.__setattr__(instance, "streaming", True)
    object.__setattr__(instance, "model", "ernie-test")
    object.__setattr__(instance, "_convert_prompt_msg_params", lambda messages, **kwargs: {})
    return instance


class WenXinLangChainInstanceTest(unittest.IsolatedAsyncioTestCase):
    def test_generate_preserves_stream_token_usage(self):
        result = build_instance()._generate([HumanMessage(content="hello")])

        self.assertEqual(result.llm_output["token_usage"], USAGE)

    async def test_agenerate_preserves_stream_token_usage(self):
        result = await build_instance()._agenerate([HumanMessage(content="hello")])

        self.assertEqual(result.llm_output["token_usage"], USAGE)


if __name__ == "__main__":
    unittest.main()
