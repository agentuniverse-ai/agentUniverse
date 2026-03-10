# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/2/26 09:47
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: openai_protocol_template.py
import datetime
import json
from queue import Queue
from typing import List, Dict

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput


class OpenAIProtocolTemplate(AgentTemplate):

    _streamed: bool = False

    def run(self, **kwargs) -> OutputObject:
        """Agent instance running entry.

        Returns:
            OutputObject: Agent execution result
        """
        kwargs = self.parse_openai_agent_input(kwargs)
        output_object = super().run(**kwargs)
        return self.parse_openai_protocol_output(output_object)

    def parse_openai_agent_input(self, agent_input):
        for key in self.openai_protocol_input_keys():
            if key not in agent_input:
                raise ValueError(f"{key} is not in agent input")
        messages = agent_input.get('messages')
        convert_messages, image_urls = self.convert_message(messages)
        content = messages[-1].get('content')

        if isinstance(content, str):
            agent_input['input'] = content
        elif isinstance(content, list):
            for item in content:
                if item.get('type') == 'text':
                    agent_input['input'] = item.get('text')
                elif item.get('type') == 'image_url':
                    image_urls.append(item.get('image_url'))
                else:
                    raise ValueError(f"{item} is not support")
        else:
            raise ValueError(f"{content} is not support")
        if len(convert_messages) > 1:
            agent_input['chat_history'] = convert_messages[0:len(convert_messages) - 1]
        if len(image_urls) > 0:
            agent_input['image_urls'] = image_urls
        return agent_input

    def openai_protocol_input_keys(self) -> list[str]:
        return [
            'messages', 'stream'
        ]

    def convert_message(self, messages: List[Dict]):
        image_urls = []
        for message in messages:
            content = message.get('content')
            if isinstance(content, list):
                text = ""
                for item in content:
                    if item.get('type') == 'text':
                        text = item.get('text')
                    elif item.get('type') == 'image_url':
                        image_urls.append(item.get('image_url'))
                message['content'] = text
            if message.get('role') == 'user':
                message['type'] = 'human'
            elif message.get('role') == 'assistant':
                message['type'] = 'ai'
        return [Message.from_dict(message) for message in messages], image_urls

    def parse_openai_protocol_output(self, output_object: OutputObject) -> OutputObject:
        res = {
            "object": "chat.completion",
            "id": FrameworkContextManager().get_context('trace_id'),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_model.info.get('name'),
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": output_object.get_data('output')
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        return OutputObject(params=res)

    def invoke_llm(self, llm: LLM, messages: list,
                   input_object: InputObject,
                   tools_schema: list[dict] = None,
                   agent_context: AgentContext = None,
                   **kwargs) -> LLMOutput:
        from agentuniverse.llm.llm_output import StreamReducer, StreamEventType

        llm_kwargs = dict(kwargs)
        if tools_schema:
            llm_kwargs['tools'] = tools_schema

        streaming = self.judge_stream(llm, **kwargs)
        if not streaming:
            self._streamed = False
            return llm.call(messages=messages, **llm_kwargs)

        self._streamed = True
        output_stream = agent_context.output_stream if agent_context else None
        reducer = StreamReducer()
        for event in llm.call(messages=messages, streaming=True, **llm_kwargs):
            reducer.feed(event)
            if event.type == StreamEventType.TEXT_DELTA and event.text_delta:
                self.add_output_stream(output_stream, event.text_delta)
        return reducer.build()

    async def async_invoke_llm(self, llm: LLM, messages: list,
                               input_object: InputObject,
                               tools_schema: list[dict] = None,
                               agent_context: AgentContext = None,
                               **kwargs) -> LLMOutput:
        from agentuniverse.llm.llm_output import StreamReducer, StreamEventType

        llm_kwargs = dict(kwargs)
        if tools_schema:
            llm_kwargs['tools'] = tools_schema

        streaming = self.judge_stream(llm, **kwargs)
        if not streaming:
            self._streamed = False
            return await llm.acall(messages=messages, **llm_kwargs)

        self._streamed = True
        output_stream = agent_context.output_stream if agent_context else None
        reducer = StreamReducer()
        async for event in await llm.acall(messages=messages, streaming=True, **llm_kwargs):
            reducer.feed(event)
            if event.type == StreamEventType.TEXT_DELTA and event.text_delta:
                self.add_output_stream(output_stream, event.text_delta)
        return reducer.build()

    def _emit_final_output(self, context: AgentContext, output_text: str) -> None:
        """Override to emit OpenAI protocol formatted output.

        If streaming already pushed tokens, only emit a trailing newline marker
        to signal the end of the stream, avoiding duplicate content.
        """
        if not context.output_stream:
            return
        if self._streamed:
            self.add_output_stream(context.output_stream, '\n\n')
            return
        output = {
            "object": "chat.completion.chunk",
            "id": FrameworkContextManager().get_context('trace_id'),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_model.info.get('name'),
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": output_text
                    },
                    "index": 0,
                }
            ]
        }
        context.output_stream.put(json.dumps(output))

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        if not output_stream:
            return
        output = {
            "object": "chat.completion.chunk",
            "id": FrameworkContextManager().get_context('trace_id'),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_model.info.get('name'),
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": agent_output
                    },
                    "index": 0,
                }
            ]
        }
        output_stream.put(json.dumps(output))

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}
