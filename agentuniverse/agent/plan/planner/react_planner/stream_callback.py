# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/13 11:03
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: stream_callback.py

import asyncio
import datetime
import json
from queue import Queue
from typing import Optional, Dict, Any, Union, List
from uuid import UUID

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk, LLMResult

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import ConversationMemoryModule
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class StreamOutPutCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(
        self, queue_stream: asyncio.Queue, color: Optional[str] = None, agent_info: dict = None, **kwargs
    ) -> None:
        """Initialize callback handler."""
        self.queueStream = queue_stream
        self.color = color
        if agent_info is None:
            agent_info = {}
        self.agent_info = agent_info

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        return

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""

    def on_agent_action(self, action: AgentAction, color: Optional[str] = None, **kwargs: Any) -> Any:
        self.queueStream.put_nowait(
            {"type": "ReAct", "data": {"output": "\nThought:" + action.log, "agent_info": self.agent_info}}
        )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        ConversationMemoryModule().add_tool_input_info(
            start_info={
                "source": self.agent_info.get("name"),
                "type": "agent",
            },
            target=serialized.get("name"),
            params={"input": input_str},
            pair_id=f"tool_{run_id.hex}",
        )

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        # add token chunk to the queue.
        self.queueStream.put_nowait({"type": "token", "data": {"chunk": chunk.text, "agent_info": self.agent_info}})

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        if observation_prefix is not None:
            self.queueStream.put_nowait(
                {"type": "ReAct", "data": {"output": "\n" + observation_prefix + output, "agent_info": self.agent_info}}
            )
        else:
            self.queueStream.put_nowait(
                {"type": "ReAct", "data": {"output": "\n Observation:" + output, "agent_info": self.agent_info}}
            )
        ConversationMemoryModule().add_tool_output_info(
            start_info={
                "source": self.agent_info.get("name"),
                "type": "agent",
            },
            target=kwargs.get("name"),
            params={"output": output},
            pair_id=f"tool_{kwargs.get('run_id').hex}",
        )

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""

    def on_agent_finish(self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any) -> None:
        """Run on agent end."""
        self.queueStream.put_nowait(
            {"type": "ReAct", "data": {"output": "\nThought:" + finish.output, "agent_info": self.agent_info}}
        )


class OpenAIProtocolStreamOutPutCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(
        self, queue_stream: asyncio.Queue, color: Optional[str] = None, agent_info: dict = None, **kwargs
    ) -> None:
        """Initialize callback handler."""
        self.queueStream = queue_stream
        self.color = color
        if agent_info is None:
            agent_info = {}
        self.agent_info = agent_info

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        output = {
            "object": "chat.completion.chunk",
            "id": FrameworkContextManager().get_context("trace_id"),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_info.get("name"),
            "choices": [
                {
                    "delta": {"role": "assistant", "content": agent_output},
                    "index": 0,
                }
            ],
        }
        output_stream.put(json.dumps(output))

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""

    # def on_agent_action(
    #         self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    # ) -> Any:
    #
    #     self.add_output_stream(self.queueStream, "\nThought:" + action.log)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        ConversationMemoryModule().add_tool_input_info(
            start_info={
                "source": self.agent_info.get("name"),
                "type": "agent",
            },
            target=serialized.get("name"),
            params={"input": input_str},
            pair_id=f"tool_{run_id.hex}",
        )

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        self.add_output_stream(self.queueStream, token)

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        if observation_prefix is not None:
            self.add_output_stream(self.queueStream, "\n" + observation_prefix + output + "\n Thought: ")
        else:
            self.add_output_stream(self.queueStream, "\n Observation: " + output + "\n Thought: ")
        ConversationMemoryModule().add_tool_output_info(
            start_info={
                "source": self.agent_info.get("name"),
                "type": "agent",
            },
            target=kwargs.get("name"),
            params={"output": output},
            pair_id=f"tool_{kwargs.get('run_id').hex}",
        )

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""

    # def on_agent_finish(
    #         self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    # ) -> None:
    #     """Run on agent end."""
    #     self.add_output_stream(self.queueStream, '\nThought:' + finish.output)


class InvokeCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    source: str
    llm_name: str

    def __init__(self, source: str, llm_name: str) -> None:
        """Initialize callback handler."""
        self.source = source
        self.llm_name = llm_name

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        prompt = "\n".join(prompts)

        start_info = {
            "source": self.source,
            "type": "agent",
        }

        ConversationMemoryModule().add_llm_input_info(start_info, self.llm_name, prompt, f"llm_{run_id.hex}")

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        start_info = {
            "source": self.source,
            "type": "agent",
        }
        ConversationMemoryModule().add_llm_output_info(
            start_info, self.llm_name, response.generations[0][0].text, f"llm_{run_id.hex}"
        )
