from typing import List, Optional, Iterator, Any, AsyncIterator

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage

from agentuniverse.llm.llm import LLM


class OllamaLangchainInstance(ChatOllama):
    llm: LLM = None

    def __init__(self, llm: LLM):
        super().__init__()
        self.llm = llm
        self.model = llm.model_name

    def _create_chat_stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        data = self.llm.call(messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs)
        for llm_output in data:
            yield llm_output.raw

    async def _acreate_chat_stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        data = await self.llm.acall(messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs)
        async for llm_output in data:
            yield llm_output.raw
