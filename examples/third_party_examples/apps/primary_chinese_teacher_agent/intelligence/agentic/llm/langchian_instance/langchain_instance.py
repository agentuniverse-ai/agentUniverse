# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/25 16:39
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: langchain_instance.py
from typing import Optional, List, Any, Iterator, AsyncIterator

from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun

from agentuniverse.llm.llm import LLM

from langchain_core.language_models import LLM as LangChainLLM

from agentuniverse.llm.llm_output import LLMOutput
from langchain_core.outputs import GenerationChunk


class LangChainInstance(LangChainLLM):
    llm: LLM = None
    llm_type: str = "AgentUniverse"
    streaming: bool = False

    def __init__(self, llm: LLM, llm_type: str, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        self.llm_type = llm_type

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any) -> str:
        should_stream = kwargs.pop("streaming", False) if "streaming" in kwargs else self.streaming
        llm_output = self.llm.call(prompt=prompt, stop=stop, **kwargs)
        if not should_stream:
            return llm_output.text
        return self.parse_stream_result(llm_output, run_manager)

    async def _acall(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        should_stream = kwargs.pop("streaming", False) if "streaming" in kwargs else self.streaming
        llm_output = await self.llm.acall(prompt=prompt, stop=stop, **kwargs)
        if not should_stream:
            return llm_output.text
        return await self.aparse_stream_result(llm_output, run_manager)

    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        kwargs['stream'] = True
        llm_output = self.llm.call(prompt=prompt, stop=stop, **kwargs)
        for line in llm_output:
            yield GenerationChunk(text=line.text, generation_info=line.raw)

    async def _astream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[GenerationChunk]:
        kwargs['stream'] = True
        llm_output = await self.llm.acall(prompt=prompt, stop=stop, **kwargs)
        async for line in llm_output:
            yield GenerationChunk(text=line.text, generation_info=line.raw)

    @staticmethod
    def parse_stream_result(stream_result: Iterator[LLMOutput],
                            run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        all_data = ""
        for line in stream_result:
            all_data += line.text
            if run_manager:
                run_manager.on_llm_new_token(line.text)
        return all_data

    @staticmethod
    async def aparse_stream_result(stream_result: AsyncIterator[LLMOutput],
                                   run_manager: Optional[AsyncCallbackManagerForLLMRun] = None) -> str:
        all_data = ""
        async for line in stream_result:
            all_data += line.text
            if run_manager:
                await run_manager.on_llm_new_token(line.text)
        return all_data

    @property
    def _llm_type(self) -> str:
        return self.llm_type

    def get_num_tokens(self, text: str) -> int:
        return self.llm.get_num_tokens(text)

    def get_token_ids(self, text: str) -> List[int]:
        return self.llm.get_token_ids(text)
