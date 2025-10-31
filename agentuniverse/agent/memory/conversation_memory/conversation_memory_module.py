# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/21 16:55
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: conversation_memory_module.py

import datetime
import json
import queue
import traceback
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from typing import List, Optional

from agentuniverse.agent.agent_manager import AgentManager

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.memory.conversation_memory.conversation_message import ConversationMessage
from agentuniverse.agent.memory.conversation_memory.enum import ConversationMessageSourceType
from agentuniverse.agent.memory.memory_manager import MemoryManager
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.logging.logging_util import LOGGER


def generate_relation_str(source: str, target: str, source_type: str, target_type: str, type: str):
    if source_type == 'agent' and target_type == 'agent' and type == 'input':
        return f"智能体 {source} 向智能体 {target} 提出了一个问题"
    if source_type == 'agent' and target_type == 'agent' and type == 'output':
        return f"智能体 {target} 回答了智能体 {source} 的问题"
    if source_type == 'agent' and target_type == 'tool' and type == 'input':
        return f"智能体 {source} 调用了工具 {target}，执行的参数是"
    if source_type == 'agent' and target_type == 'tool' and type == 'output':
        return f"工具 {target} 返回给智能体 {source} 的执行结果"
    if source_type == 'agent' and target_type == 'knowledge' and type == 'input':
        return f"智能体 {source} 在知识库 {target} 中进行了搜索，关键词是"
    if source_type == 'agent' and target_type == 'knowledge' and type == 'output':
        return f"知识库 {target} 返回给智能体 {source} 的搜索结果"
    if source_type == 'agent' and target_type == 'llm' and type == 'input':
        return f"智能体 {source} 向大模型 {target} 提问"
    if source_type == 'agent' and target_type == 'llm' and type == 'output':
        return f"大模型 {target} 返回给智能体 {source} 的答案"
    if source_type == 'unknown' and target_type == 'agent' and type == 'input':
        return f"未知类型 {source} 向智能体 {target} 提出了一个问题"
    if source_type == 'unknown' and target_type == 'agent' and type == 'output':
        return f"智能体 {target} 回答了未知 {source} 的问题"
    if source_type == "user" and target_type == 'agent' and type == 'input':
        return f"用户向智能体 {target} 提出了一个问题"
    if source_type == 'user' and target_type == 'agent' and type == 'output':
        return f"智能体 {target} 回答了用户的问题"
    elif type == 'input':
        return f"{source} 向 {target} 询问了一个问题"
    elif type == 'output':
        return f"{source} 回答了 {target} 的问题"
    elif type == 'summary':
        return f"{source} 的摘要"
    return None


def generate_relation_str_en(source: str, target: str, source_type: str, target_type: str, type: str):
    if source_type == 'agent' and target_type == 'agent' and type == 'input':
        return f"Agent {source} asked a question to agent {target}"
    if source_type == 'agent' and target_type == 'agent' and type == 'output':
        return f"Agent {target} answered the question asked by agent {source}"
    if source_type == 'agent' and target_type == 'tool' and type == 'input':
        return f"Agent {source} called tool {target}, the parameters are"
    if source_type == 'agent' and target_type == 'tool' and type == 'output':
        return f"Tool {target} returned the result to agent {source}"
    if source_type == 'agent' and target_type == 'knowledge' and type == 'input':
        return f"Agent {source} searched in knowledge {target}, the keywords are"
    if source_type == 'agent' and target_type == 'knowledge' and type == 'output':
        return f"Knowledge {target} returned the result to agent {target}"
    if source_type == 'agent' and target_type == 'llm' and type == 'input':
        return f"Agent {source} asked a question to llm {target}"
    if source_type == 'agent' and target_type == 'llm' and type == 'output':
        return f"LLM {target} returned the answer to agent {source}"
    if source_type == 'unknown' and target_type == 'agent' and type == 'input':
        return f"Unknown type {source} asked a question to agent {target}"
    if source_type == 'unknown' and target_type == 'agent' and type == 'output':
        return f"Agent {target} answered the unknown {source} question"
    if source_type == "user" and target_type == 'agent' and type == 'input':
        return f"User asked a question to agent {target}"
    if source_type == 'user' and target_type == 'agent' and type == 'output':
        return f"Agent {target} answered the user's question"
    if type == 'input':
        return f"{source} asked a question to {target}"
    elif type == 'output':
        return f"{target} answered {source}'s question"
    elif type == 'summary':
        return f"{source} summary"
    return None


def sync_to_sub_agent_memory(message: ConversationMessage, session_id: str, memory_name: str):
    def add_message(agent_name: str, memory_names: list, collect_type: str):
        agent_instance = AgentManager().get_instance_obj(agent_name)
        agent_memory = agent_instance.agent_model.memory.get('conversation_memory')
        collection_types = agent_instance.agent_model.memory.get('collection_types')
        if collection_types and collect_type not in collection_types:
            return
        if agent_memory:
            memory_instance = MemoryManager().get_instance_obj(agent_memory)
            memory_instance.add([message], session_id=session_id)
            memory_names.append(agent_memory)

    memory_names = [memory_name]
    if message.source_type == ConversationMessageSourceType.AGENT.value:
        add_message(message.source, memory_names, message.target_type)

    if message.target_type == ConversationMessageSourceType.AGENT.value:
        add_message(message.target, memory_names, message.source_type)


@singleton
class ConversationMemoryModule:

    def __init__(self):
        conversation_memory_configer = ApplicationConfigManager().app_configer.conversation_memory_configer
        self.instance_name = conversation_memory_configer.get('instance_name', '')
        self.activate = conversation_memory_configer.get('activate', False)
        self.logging = conversation_memory_configer.get('logging', False)
        self.collection_types = conversation_memory_configer.get('collection_types', ['agent', 'user'])
        self.conversation_format = conversation_memory_configer.get('conversation_format', 'cn')
        self.max_content_length = conversation_memory_configer.get('max_content_length', 8000)
        self.queue = queue.Queue(1000)
        self.thread_pool = ThreadPoolExecutor(max_workers=conversation_memory_configer.get('thread_pool', 4))
        Thread(target=self._consume_queue, daemon=True).start()

    def _consume_queue(self):
        while True:
            func = self.queue.get()
            try:
                self.thread_pool.submit(func)
            except Exception as e:
                LOGGER.error(f"Failed to process trace info: {e}")
                # Print full traceback for debugging
                traceback.print_exc()
            finally:
                self.queue.task_done()

    def _add_trace_info(self, source: str,
                        source_type: str,
                        target: str,
                        target_type: str,
                        type: str,
                        params: dict, **kwargs) -> None:
        if not self.activate:
            return
        content = None
        if type == "input" and target_type == 'agent':
            agent_instance = AgentManager().get_instance_obj(target)
            input_field = agent_instance.agent_model.memory.get('input_field')
            if input_field and input_field in params:
                content = params.get(input_field)
        elif type == "output" and source_type == 'agent':
            agent_instance = AgentManager().get_instance_obj(source)
            output_field = agent_instance.agent_model.memory.get('output_field')
            if output_field and output_field in params:
                content = params.get(output_field)

        if content is None and type in params:
            content = params[type]
        elif content is None:
            try:
                content = json.dumps(params, ensure_ascii=False)
            except Exception as e:
                content = str(e)
        try:
            params_json = json.dumps(params, ensure_ascii=False)
        except Exception as e:
            params_json = json.dumps({
                "error": str(e)
            }, ensure_ascii=False)
        if self.conversation_format == 'cn':
            prefix = generate_relation_str(source, target, source_type, target_type, type)
        else:
            prefix = generate_relation_str_en(source, target, source_type, target_type, type)
        if not prefix:
            return
        if isinstance(content, str) and len(content) > self.max_content_length:
            content = content[:self.max_content_length]
        if len(params_json) > self.max_content_length:
            params_json = params_json[:self.max_content_length]
        if self.logging:
            LOGGER.info(
                f"{kwargs.get('session_id')} | {kwargs.get('trace_id')}| {kwargs.get('pair_id')} |\n {prefix}:{content}")
        message = ConversationMessage(
            id=uuid.uuid4().hex,
            conversation_id=kwargs.get('session_id'),
            trace_id=kwargs.get('trace_id'),
            source=source,
            source_type=source_type,
            target=target,
            target_type=target_type,
            type=type,
            metadata={
                "timestamp": datetime.datetime.now(),
                "prefix": prefix,
                "params": params_json,
                "pair_id": kwargs.get('pair_id'),
                'gmt_created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            content=f"{content}"
        )
        if self.instance_name:
            memory = MemoryManager().get_instance_obj(self.instance_name)
            if memory:
                memory.add([message], session_id=kwargs.get('session_id'))
        sync_to_sub_agent_memory(message, kwargs.get('session_id'), self.instance_name)

    def _add_trace(self, start_info, target_info: dict, type: str, params: dict, session_id: str, trace_id: str,
                   pair_id: str):
        if "kwargs" in params:
            params = params['kwargs']
        if params is str:
            params = {
                type: params
            }

        kwargs = {'source': start_info['source'], 'source_type': start_info['type'], 'target': target_info['source'],
                  'target_type': target_info['type'], 'type': type, 'params': params, 'trace_id': trace_id,
                  'session_id': session_id,
                  "pair_id": pair_id}
        self._add_trace_info(**kwargs)

    def add_trace_info(self, start_info: dict, target_info: dict, type: str, params: dict, pair_id: str):
        """Add trace info to the memory."""
        trace_id = FrameworkContextManager().get_context('trace_id')
        if trace_id is None:
            trace_id = str(uuid.uuid4())
            FrameworkContextManager().set_context('trace_id', trace_id)

        session_id = FrameworkContextManager().get_context('session_id')
        if session_id is None:
            session_id = str(uuid.uuid4())
            FrameworkContextManager().set_context('session_id', session_id)
        def add_trace():
            self._add_trace(start_info, target_info, type, params, session_id,
                            trace_id, pair_id)

        self.queue.put_nowait(add_trace)

    def add_tool_input_info(self, start_info: dict, target: str, params: dict, pair_id: str, auto: bool = True):
        """Add trace info to the memory."""

        if not self.collection_current_agent_memory(start_info, 'tool', auto):
            return

        target_info = {'source': target, 'type': 'tool'}
        self.add_trace_info(start_info, target_info, 'input', params, pair_id)

    def add_tool_output_info(self, start_info: dict, target: str, params: dict, pair_id: str, auto: bool = True):
        """Add trace info to the memory."""
        if not self.collection_current_agent_memory(start_info, 'tool', auto):
            return

        target_info = {'source': target, 'type': 'tool'}
        self.add_trace_info(start_info, target_info, 'output', params, pair_id)

    def add_knowledge_input_info(self, start_info: dict, target: str, params: dict, pair_id: str, auto: bool = True):

        if not self.collection_current_agent_memory(start_info, 'knowledge', auto):
            return

        target_info = {'source': target, 'type': 'knowledge'}
        self.add_trace_info(start_info, target_info, 'input', params, pair_id)

    def add_knowledge_output_info(self, start_info: dict, target: str, params: List[Document], pair_id: str,
                                  auto: bool = True):

        if not self.collection_current_agent_memory(start_info, 'knowledge', auto):
            return
        target_info = {'source': target, 'type': 'knowledge'}
        doc_data = []
        for doc in params:
            doc_data.append(doc.text)
        self.add_trace_info(start_info, target_info, 'output', {
            'output': "\n==============================\n".join(doc_data)
        }, pair_id)

    def add_agent_input_info(self, start_info: dict, instance: 'Agent', params: dict, pair_id: str,
                             auto: bool = True):
        if auto:
            if not instance.collect_current_memory(start_info.get('type')):
                return
            if not self.activate:
                return
            if 'agent' not in self.collection_types:
                return

        target_info = {'source': instance.agent_model.info.get('name'), 'type': 'agent'}
        input_keys = instance.input_keys()
        if "kwargs" in params:
            params: dict = params['kwargs']
            params = params.copy()
            params.pop('output_stream') if 'output_stream' in params else params
        if auto:
            params = {key: params[key] for key in input_keys}
        self.add_trace_info(start_info, target_info, 'input', params, pair_id)

    def add_agent_result_info(self, agent_instance: 'Agent', agent_result: Optional[OutputObject | dict],
                              target_info: dict,
                              pair_id: str, auto: bool = True):

        if auto:
            if not agent_instance.collect_current_memory(target_info.get('type')):
                return
            if not self.activate:
                return
            if 'agent' not in self.collection_types:
                return

        trace_id = FrameworkContextManager().get_context('trace_id')
        session_id = FrameworkContextManager().get_context('session_id')

        def add_trace():
            output_keys = agent_instance.output_keys()
            if auto:
                params = {key: agent_result.get_data(key) for key in output_keys}
            else:
                params = agent_result
            start_info = {
                "source": agent_instance.agent_model.info.get('name'),
                "type": "agent"
            }
            self._add_trace(target_info, start_info, 'output', params, session_id, trace_id, pair_id)
        self.queue.put_nowait(add_trace)

    def add_llm_input_info(self, start_info: dict, target: str, prompt: str, pair_id: str, auto=True):
        if not self.collection_current_agent_memory(start_info, 'llm', auto):
            return

        target_info = {'source': target, 'type': 'llm'}
        self.add_trace_info(start_info, target_info, 'input', {'input': prompt}, pair_id)

    def add_llm_output_info(self, start_info: dict, target: str, output: str, pair_id: str, auto=True):
        if not self.collection_current_agent_memory(start_info, 'llm', auto):
            return
        target_info = {'source': target, 'type': 'llm'}
        self.add_trace_info(start_info, target_info, 'output', {
            'output': output
        }, pair_id)

    def collection_current_agent_memory(self, info: dict, collection_type: str, auto: bool):
        if not auto:
            return True
        if not self.activate:
            return False
        if info.get('type') == 'agent':
            agent_id = info.get('source')
            agent_instance = AgentManager().get_instance_obj(agent_id)
            if agent_instance:
                collection_types = agent_instance.agent_model.memory.get('collection_types')
                res = agent_instance.collect_current_memory(collection_type)
                if not res:
                    return False
                if collection_types:
                    return res
        if collection_type not in self.collection_types:
            return False
        return True
