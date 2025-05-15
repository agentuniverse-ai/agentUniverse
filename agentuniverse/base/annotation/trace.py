# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/5 15:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: trace.py
import asyncio
import functools
import inspect
import time
import uuid

from functools import wraps

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import ConversationMemoryModule
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput


def trace_llm(func):
    """Annotation: @trace_llm

    Decorator to trace the LLM invocation, add llm input and output to the monitor.
    """
    def plugins(func):
        llm_plugins = ApplicationConfigManager().app_configer.llm_plugins
        warp_func = func
        for item in llm_plugins:
            warp_func = item(func)
        return warp_func

    @wraps(func)
    async def wrapper_async(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_input(func, *args, **kwargs)

        source = func.__qualname__

        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)

        if self and hasattr(self, 'name'):
            name = self.name
            if name is not None:
                source = name

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return await plugins(func)(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'llm'})

        start_time = time.time()
        Monitor().trace_llm_input(source=source, llm_input=llm_input)

        # invoke function
        result = await plugins(func)(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input, llm_output=result.text,
                                           cost_time=time.time() - start_time)

            # add llm token usage to monitor
            Monitor().trace_llm_token_usage(self, llm_input, result.text)
            Monitor.pop_invocation_chain()
            return result
        else:
            # streaming
            async def gen_iterator():
                llm_output = []
                async for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                output_str = "".join(llm_output)
                Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                               llm_output=output_str, cost_time=time.time() - start_time)
                # add llm token usage to monitor
                Monitor().trace_llm_token_usage(self, llm_input, output_str)
                Monitor.pop_invocation_chain()

            return gen_iterator()

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_input(func, *args, **kwargs)

        source = func.__qualname__

        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)

        if self and hasattr(self, 'name'):
            name = self.name
            if name is not None:
                source = name

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return plugins(func)(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'llm'})

        start_time = time.time()
        Monitor().trace_llm_input(source=source, llm_input=llm_input)
        # invoke function
        result = plugins(func)(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            Monitor().trace_llm_invocation(source=source, llm_input=llm_input, llm_output=result.text,
                                           cost_time=time.time() - start_time)

            # add llm token usage to monitor
            Monitor().trace_llm_token_usage(self, llm_input, result.text)
            Monitor.pop_invocation_chain()
            return result
        else:
            # streaming
            def gen_iterator():
                llm_output = []
                for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                output_str = "".join(llm_output)
                Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                               llm_output=output_str, cost_time=time.time() - start_time)

                # add llm token usage to monitor
                Monitor().trace_llm_token_usage(self, llm_input, output_str)
                Monitor.pop_invocation_chain()

            return gen_iterator()

    if asyncio.iscoroutinefunction(func):

        return wrapper_async
    else:
        return wrapper_sync


def get_caller_info(instance: object = None):
    source_list = Monitor.get_invocation_chain()
    if len(source_list) > 0:
        return {
            'source': source_list[-1].get('source'),
            'type': source_list[-1].get('type')
        }
    else:
        return {
            'source': '',
            'type': 'user'
        }


def trace_agent(func):
    """Annotation: @trace_agent

    Decorator to trace the agent invocation, add agent input and output to the monitor.
    """

    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        # get agent input from arguments
        agent_input = _get_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        source = func.__qualname__
        self = agent_input.pop('self', None)

        tracing = None
        if isinstance(self, object):
            agent_model = getattr(self, 'agent_model', None)
            if isinstance(agent_model, object):
                info = getattr(agent_model, 'info', None)
                profile = getattr(agent_model, 'profile', None)
                if isinstance(info, dict):
                    source = info.get('name', None)
                if isinstance(profile, dict):
                    tracing = profile.get('tracing', None)
        start_info = get_caller_info()
        pair_id = f"agent_{uuid.uuid4().hex}"
        kwargs['memory_source_info'] = start_info
        # add invocation chain to the monitor module.
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': source, 'type': 'agent'})
        ConversationMemoryModule().add_agent_input_info(start_info, self, agent_input, pair_id)
        if tracing is False:
            result = await func(*args, **kwargs)
            ConversationMemoryModule().add_agent_result_info(self, result, start_info, pair_id)
            Monitor.pop_invocation_chain()
            return result

        start_time = time.time()
        Monitor().trace_agent_input(source=source, agent_input=agent_input)

        # invoke function
        result = await func(*args, **kwargs)
        # add agent invocation info to monitor
        Monitor().trace_agent_invocation(source=source, agent_input=agent_input, agent_output=result,
                                         cost_time=time.time() - start_time)
        ConversationMemoryModule().add_agent_result_info(self, result, start_info, pair_id)
        Monitor.pop_invocation_chain()
        return result

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get agent input from arguments
        agent_input = _get_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        source = func.__qualname__
        self = agent_input.pop('self', None)

        tracing = None
        if isinstance(self, object):
            agent_model = getattr(self, 'agent_model', None)
            if isinstance(agent_model, object):
                info = getattr(agent_model, 'info', None)
                profile = getattr(agent_model, 'profile', None)
                if isinstance(info, dict):
                    source = info.get('name', None)
                if isinstance(profile, dict):
                    tracing = profile.get('tracing', None)
        pair_id = f"agent_{uuid.uuid4().hex}"
        start_info = get_caller_info()
        kwargs['memory_source_info'] = start_info
        # add invocation chain to the monitor module.
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': source, 'type': 'agent'})
        ConversationMemoryModule().add_agent_input_info(start_info, self, agent_input, pair_id)
        if tracing is False:
            result = func(*args, **kwargs)
            ConversationMemoryModule().add_agent_result_info(self, result, start_info, pair_id)
            Monitor.pop_invocation_chain()
            return result

        start_time = time.time()
        Monitor().trace_agent_input(source=source, agent_input=agent_input)

        # invoke function
        result = func(*args, **kwargs)
        # add agent invocation info to monitor
        Monitor().trace_agent_invocation(source=source, agent_input=agent_input, agent_output=result,
                                         cost_time=time.time() - start_time)
        ConversationMemoryModule().add_agent_result_info(self, result, start_info, pair_id)
        Monitor.pop_invocation_chain()
        return result

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


def trace_tool(func):
    """Annotation: @trace_tool

    A decorator to trace tool invocations, supporting both synchronous and asynchronous functions.
    It monitors tool execution, tracks timing, and maintains an invocation chain.
    """

    def process_tool(source, tool_input, start_info, pair_id):
        """Process common tool logic

        Args:
            source: The source/name of the tool
            tool_input: Input parameters for the tool
            start_info: Information about where the tool was called from
            pair_id: The ID for this tool invocation

        Returns:
            tuple: (self tool instance, updated source name)
        """
        self = tool_input.pop('self', None)
        if isinstance(self, object):
            name = getattr(self, 'name', None)
            if name is not None:
                source = name
        ConversationMemoryModule().add_tool_input_info(start_info, source, tool_input, pair_id)
        return self, source

    def handle_tool_result(start_info, source, result, pair_id):
        """Handle the tool execution result

        Args:
            start_info: Information about where the tool was called from
            source: The source/name of the tool
            result: The execution result
            pair_id: The ID for this tool invocation

        Returns:
            The execution result
        """
        ConversationMemoryModule().add_tool_output_info(start_info, source, params=result, pair_id=pair_id)
        return result

    def trace_tool_execution(source, tool_input, result, start_time):
        """Trace the tool execution process

         Args:
             source: The source/name of the tool
             tool_input: Input parameters for the tool
             result: The execution result
             start_time: Timestamp when the tool execution started
         """
        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'tool'})
        Monitor().trace_tool_invocation(
            source=source,
            tool_input=tool_input,
            tool_output=result,
            cost_time=time.time() - start_time
        )
        Monitor.pop_invocation_chain()

    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        # Extract tool input from arguments
        tool_input = _get_input(func, *args, **kwargs)
        start_time = time.time()
        source = func.__qualname__
        start_info = get_caller_info()
        pair_id = f"tool_{uuid.uuid4().hex}"

        self, source = process_tool(source, tool_input, start_info, pair_id)

        # Handle case when tracing is disabled
        if self and hasattr(self, 'tracing') and self.tracing is False:
            result = await func(*args, **kwargs)
            return handle_tool_result(start_info, source, result, pair_id)

        # Initialize and execute with full tracing
        Monitor.init_invocation_chain()
        Monitor().trace_tool_input(source, tool_input)
        result = await func(*args, **kwargs)
        trace_tool_execution(source, tool_input, result, start_time)
        return handle_tool_result(start_info, source, result, pair_id)

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # Extract tool input from arguments
        tool_input = _get_input(func, *args, **kwargs)
        start_time = time.time()
        source = func.__qualname__
        start_info = get_caller_info()
        pair_id = f"tool_{uuid.uuid4().hex}"

        self, source = process_tool(source, tool_input, start_info, pair_id)

        # Handle case when tracing is disabled
        if self and hasattr(self, 'tracing') and self.tracing is False:
            result = func(*args, **kwargs)
            return handle_tool_result(start_info, source, result, pair_id)

        # Initialize and execute with full tracing
        Monitor.init_invocation_chain()
        Monitor().trace_tool_input(source, tool_input)
        result = func(*args, **kwargs)
        trace_tool_execution(source, tool_input, result, start_time)
        return handle_tool_result(start_info, source, result, pair_id)

    return wrapper_async if asyncio.iscoroutinefunction(func) else wrapper_sync


def trace_knowledge(func):
    """Annotation: @trace_knowledge

    Decorator to trace the knowledge invocation.
    """

    def process_knowledge(source, knowledge_input, start_info, pair_id):
        """Process common knowledge logic

        Args:
            source: The source/name of the knowledge
            knowledge_input: Input parameters for the knowledge
            start_info: Information about where the knowledge was called from
            pair_id: The ID for this knowledge invocation

        Returns:
            tuple: (self knowledge instance, updated source name)
        """
        self = knowledge_input.pop('self', None)
        if isinstance(self, object):
            name = getattr(self, 'name', None)
            if name is not None:
                source = name
        ConversationMemoryModule().add_knowledge_input_info(start_info, source, knowledge_input, pair_id)
        return self, source

    def handle_knowledge_result(start_info, source, result, pair_id):
        """Handle the knowledge execution result

        Args:
            start_info: Information about where the knowledge was called from
            source: The source/name of the knowledge
            result: The execution result
            pair_id: The ID for this knowledge invocation

        Returns:
            The execution result
        """
        ConversationMemoryModule().add_knowledge_output_info(start_info, source, params=result, pair_id=pair_id)
        return result

    def trace_knowledge_execution(source):
        """Trace the knowledge execution process

        Args:
            source: The source/name of the knowledge
        """
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': source, 'type': 'knowledge'})

    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        # Get knowledge input from arguments
        knowledge_input = _get_input(func, *args, **kwargs)
        source = func.__qualname__
        start_info = get_caller_info()
        pair_id = f"knowledge_{uuid.uuid4().hex}"

        self, source = process_knowledge(source, knowledge_input, start_info, pair_id)

        # Handle case when tracing is disabled
        if self and hasattr(self, 'tracing') and self.tracing is False:
            result = await func(*args, **kwargs)
            return handle_knowledge_result(start_info, source, result, pair_id)

        # Initialize and execute with full tracing
        trace_knowledge_execution(source)
        result = await func(*args, **kwargs)
        Monitor.pop_invocation_chain()
        return handle_knowledge_result(start_info, source, result, pair_id)

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # Get knowledge input from arguments
        knowledge_input = _get_input(func, *args, **kwargs)
        source = func.__qualname__
        start_info = get_caller_info()
        pair_id = f"knowledge_{uuid.uuid4().hex}"

        self, source = process_knowledge(source, knowledge_input, start_info, pair_id)

        # Handle case when tracing is disabled
        if self and hasattr(self, 'tracing') and self.tracing is False:
            result = func(*args, **kwargs)
            return handle_knowledge_result(start_info, source, result, pair_id)

        # Initialize and execute with full tracing
        trace_knowledge_execution(source)
        result = func(*args, **kwargs)
        Monitor.pop_invocation_chain()
        return handle_knowledge_result(start_info, source, result, pair_id)

    return wrapper_async if asyncio.iscoroutinefunction(func) else wrapper_sync


def _get_input(func, *args, **kwargs) -> dict:
    """Get the agent input from arguments."""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return {k: v for k, v in bound_args.arguments.items()}
