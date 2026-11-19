from typing import List, Optional, Iterator, Any, AsyncIterator

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage

from agentuniverse.llm.llm import LLM


class OllamaLangchainInstance(ChatOllama):
    """LangChain ChatOllama instance bound to an agentUniverse LLM.

    Delegates model name and chat requests to the wrapped agentUniverse
    ``llm`` while keeping the LangChain ``ChatOllama`` streaming interface.
    """
    llm: LLM = None

    def __init__(self, llm: LLM):
        """Initialize the instance with the given agentUniverse LLM.

        Args:
            llm (LLM): the agentUniverse LLM instance to wrap.
        """
        super().__init__()
        self.llm = llm
        self.model = llm.model_name

    def _create_chat_stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> Iterator[str]:
        """Create a synchronous token stream from the wrapped LLM.

        Args:
            messages (List[BaseMessage]): chat messages to send.
            stop (Optional[List[str]]): optional stop sequences.
        Yields:
            Iterator[str]: raw text chunks produced by the LLM call.
        """
        data = self.llm.call(
            messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs
        )
        for llm_output in data:
            yield llm_output.raw

    async def _acreate_chat_stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Create an asynchronous token stream from the wrapped LLM.

        Args:
            messages (List[BaseMessage]): chat messages to send.
            stop (Optional[List[str]]): optional stop sequences.
        Yields:
            AsyncIterator[str]: raw text chunks produced by the LLM call.
        """
        data = await self.llm.acall(
                messages=self._convert_messages_to_ollama_messages(messages), stop=stop, **kwargs
        )
        async for llm_output in data:
            yield llm_output.raw
