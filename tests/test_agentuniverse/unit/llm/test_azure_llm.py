# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import unittest

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.default.azure_openai_llm import AzureOpenAILLM


# @Time    : 2025/11/11 11:03
# @Author  : xieshenghao
# @Email   : xieshenghao.xsh@antgroup.com
# @FileName: test_azure_llm.py

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant.",
    },
    {
        "role": "user",
        "content": "I am going to Paris, what should I see?",
    }
]

class AzureLLMTest(unittest.TestCase):

    def setUp(self):
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer
        self.llm = AzureOpenAILLM(
            azure_openai_endpoint=get_from_env("AZURE_OPENAI_ENDPOINT"),
            azure_openai_api_key=get_from_env("AZURE_OPENAI_API_KEY"),
            azure_api_version=get_from_env("AZURE_API_VERSION"),
        )

    def test_call(self) -> None:
        output = self.llm.call(messages)

        self.assertIsNotNone(output, "The output should not be None")


    def test_call_stream(self) -> None:

        for chunk in self.llm.call(messages=messages, streaming_usage=True):
            self.assertIsNotNone(chunk.text, "The output should not be None")

    def test_acall(self) -> None:
        output = asyncio.run(self.llm.acall(messages=messages, streaming_usage=False))
        self.assertIsNotNone(output.__str__(), "The output should not be None")

    def test_acall_stream(self):
        asyncio.run(self.acall_stream(messages=messages))

    async def acall_stream(self, messages: list):
        async for chunk in await self.llm.acall(messages=messages, streaming_usage=True):
            self.assertIsNotNone(chunk, "The output should not be None")