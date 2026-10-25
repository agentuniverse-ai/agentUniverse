# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/5 15:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: trace.py
import asyncio
import functools
import inspect
import uuid
from contextvars import ContextVar
from functools import wraps

from opentelemetry import context as otel_context

from agentuniverse.agent.memory.conversation_memory.conversation_memory_module import \
    ConversationMemoryModule
from agentuniverse.base.context.framework_context_manager import \
    FrameworkContextManager
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput


def get_caller_info(instance: object = None):
    source_list = Monitor.get_invocation_chain()
    if len(source_list) > 0:
        return {
            'source': source_list[-1].get('source'),
            'type': source_list[-1].get('type')
        }
    else:
        return {
            'source': 'unknown',
            'type': 'user'
        }


def _get_input(func, *args, **kwargs) -> dict:
    """Get the agent input from arguments."""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return {k: v for k, v in bound_args.arguments.items()}


class InvocationChainContext:
    def __init__(self, source, node_type):
        self.source = source
        self.node_type = node_type

    def __enter__(self):
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': self.source, 'type': self.node_type})

    def __exit__(self, *args):
        Monitor.pop_invocation_chain()


# llm trace

def _llm_plugins(func):
    llm_plugins = ApplicationConfigManager().app_configer.llm_plugins
    warp_func = func
    for item in llm_plugins:
        warp_func = item(func)
    return warp_func


def _get_llm_info(func, *args, **kwargs):
    llm_input = _get_input(func, *args, **kwargs)

    model_name = func.__qualname__

    # check whether the tracing switch is enabled
    self = llm_input.pop('self', None)

    if self and hasattr(self, 'name'):
        name = self.name
        if name is not None:
            model_name = name

    channel_name = 'default_channel'
    if self and hasattr(self, 'channel_name'):
        channel_name = self.channel_name
        if channel_name is not None:
            channel_name = channel_name

    caller_info = get_caller_info()


    temperature = kwargs.get('temperature')
    if temperature is None and self and hasattr(self, 'channel_model_config'):
        temperature = self.channel_model_config.get('temperature')
    if temperature is None and self and hasattr(self, 'temperature'):
        temperature = self.temperature
    if temperature is None:
        temperature = -1

    params = {
        'temperature': temperature,
    }

    return self, model_name, channel_name, llm_input, params, caller_info


async def _default_llm_wrapper_async(func, *args, **kwargs):
    # get llm input from arguments
    self, source, _, llm_input, _, _ = _get_llm_info(func, *args, **kwargs)

    # add invocation chain to the monitor module.
    Monitor.add_invocation_chain({'source': source, 'type': 'llm'})
    result = await _llm_plugins(func)(*args, **kwargs)
    # not streaming
    if isinstance(result, LLMOutput):
        Monitor.pop_invocation_chain()
        return result
    else:
        # streaming
        async def gen_iterator():
            try:
                async for chunk in result:
                    yield chunk
            finally:
                # add llm invocation info to monitor
                # runs also when the consumer aborts the stream early
                Monitor.pop_invocation_chain()

        return gen_iterator()


def _default_llm_wrapper_sync(func, *args, **kwargs):
    # get llm input from arguments
    self, source, _, llm_input, _, _ = _get_llm_info(func, *args, **kwargs)

    # add invocation chain to the monitor module.
    Monitor.add_invocation_chain({'source': source, 'type': 'llm'})
    # invoke function
    result = _llm_plugins(func)(*args, **kwargs)
    # not streaming
    if isinstance(result, LLMOutput):
        Monitor.pop_invocation_chain()
        return result
    else:
        # streaming
        def gen_iterator():
            try:
                for chunk in result:
                    yield chunk
            finally:
                # add llm invocation info to monitor
                # runs also when the consumer aborts the stream early
                Monitor.pop_invocation_chain()

        return gen_iterator()


_llm_wrapper_async = _default_llm_wrapper_async
_llm_wrapper_sync = _default_llm_wrapper_sync


def trace_llm(func):
    """Annotation: @trace_llm

    Decorator to trace the LLM invocation, add llm input and output to the monitor.
    """

    @wraps(func)
    async def wrapper_async(*args, **kwargs):
        impl = globals().get('_llm_wrapper_async',
                             _default_llm_wrapper_async)
        return await impl(func, *args, **kwargs)

    @wraps(func)
    def wrapper_sync(*args, **kwargs):
        impl = globals().get('_llm_wrapper_sync',
                             _default_llm_wrapper_sync)
        return impl(func, *args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return wrapper_async
    else:
        return wrapper_sync


# trace agent

# Depth of traced agent runs in the current execution context. Framework
# context cleanup only happens when the outermost traced agent run finishes.
_agent_scope_depth = ContextVar('_agent_scope_depth', default=0)

_REQUEST_FRAMEWORK_CONTEXT_KEYS = ('session_id', 'trace_id')
_FRAMEWORK_TRACE_KEY_SUFFIXES = ('_invocation_chain', '_invocation_chain_bak',
                                 '_token_usage')


def _is_trace_state_key(key: str) -> bool:
    return key.endswith(_FRAMEWORK_TRACE_KEY_SUFFIXES)


def _has_meaningful_state(value) -> bool:
    """Empty monitor state is treated as absent.

    Monitor.get_invocation_chain lazily creates an empty chain entry when
    read, so an empty list must not count as pre-existing state that has to
    survive the traced run.
    """
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return value is not None


def _snapshot_request_framework_context() -> dict:
    """Capture the request-scoped framework context state.

    'session_id' and 'trace_id' may be generated and persisted into the
    thread level framework context while a request runs (for example by
    ConversationMemoryModule.add_trace_info), and monitor state is stored
    under per-trace keys. Without restoring them, a reused server thread
    keeps the previous request's session for the next request and the trace
    state keys accumulate forever.
    """
    manager = FrameworkContextManager()
    snapshot = {key: manager.get_context(key)
                for key in _REQUEST_FRAMEWORK_CONTEXT_KEYS
                if manager.is_context_exist(key)}
    for key in list(manager.context_dict.keys()):
        if _is_trace_state_key(key):
            value = manager.get_context(key)
            if _has_meaningful_state(value):
                snapshot[key] = value
    return snapshot


def _restore_request_framework_context(snapshot: dict):
    """Restore the request-scoped framework context state.

    Pre-existing entries (e.g. a chain set up by an enclosing caller) are
    restored to their captured value; entries created during the traced run
    are removed.
    """
    manager = FrameworkContextManager()
    for key in _REQUEST_FRAMEWORK_CONTEXT_KEYS:
        if key in snapshot:
            manager.set_context(key, snapshot[key])
        else:
            manager.del_context(key, force=True)
    for key in list(manager.context_dict.keys()):
        if _is_trace_state_key(key):
            if key in snapshot:
                manager.set_context(key, snapshot[key])
            else:
                manager.del_context(key, force=True)


def _get_agent_info(func, *args, **kwargs):
    agent_input = _get_input(func, *args, **kwargs)
    source = func.__qualname__
    self = agent_input.pop('self', None)
    start_info = get_caller_info()
    pair_id = f"agent_{uuid.uuid4().hex}"

    if isinstance(self, object):
        agent_model = getattr(self, 'agent_model', None)
        if isinstance(agent_model, object):
            info = getattr(agent_model, 'info', None)
            if isinstance(info, dict):
                source = info.get('name', None)

    return self, source, agent_input, start_info, pair_id


async def _default_agent_wrapper_async(func, *args, **kwargs):
    agent_instance, source, agent_input, start_info, pair_id = _get_agent_info(
        func, *args, **kwargs)
    # Agent.run may attach an OTel context derived from a caller-supplied
    # trace_id. Restore the previous context afterwards so server threads do
    # not carry one request's trace into the next request.
    saved_otel_context = otel_context.get_current()
    is_outermost = _agent_scope_depth.get() == 0
    saved_framework_context = (_snapshot_request_framework_context()
                               if is_outermost else None)
    depth_token = _agent_scope_depth.set(_agent_scope_depth.get() + 1)
    try:
        with InvocationChainContext(source=source, node_type='agent'):
            kwargs['memory_source_info'] = start_info
            ConversationMemoryModule().add_agent_input_info(start_info,
                                                            agent_instance,
                                                            agent_input,
                                                            pair_id)
            result = await func(*args, **kwargs)
            ConversationMemoryModule().add_agent_result_info(agent_instance,
                                                             result,
                                                             start_info,
                                                             pair_id)
            return result
    finally:
        _agent_scope_depth.reset(depth_token)
        otel_context.attach(saved_otel_context)
        if is_outermost:
            _restore_request_framework_context(saved_framework_context)


def _default_agent_wrapper_sync(func, *args, **kwargs):
    # get agent input from arguments
    agent_instance, source, agent_input, start_info, pair_id = _get_agent_info(
        func, *args, **kwargs)
    # See _default_agent_wrapper_async: restore the OTel context that was
    # current before this traced agent run, and clear request-scoped
    # framework context entries at the outermost run.
    saved_otel_context = otel_context.get_current()
    is_outermost = _agent_scope_depth.get() == 0
    saved_framework_context = (_snapshot_request_framework_context()
                               if is_outermost else None)
    depth_token = _agent_scope_depth.set(_agent_scope_depth.get() + 1)
    try:
        with InvocationChainContext(source=source, node_type='agent'):
            kwargs['memory_source_info'] = start_info
            ConversationMemoryModule().add_agent_input_info(start_info,
                                                            agent_instance,
                                                            agent_input,
                                                            pair_id)
            result = func(*args, **kwargs)
            ConversationMemoryModule().add_agent_result_info(agent_instance,
                                                             result,
                                                             start_info,
                                                             pair_id)
            return result
    finally:
        _agent_scope_depth.reset(depth_token)
        otel_context.attach(saved_otel_context)
        if is_outermost:
            _restore_request_framework_context(saved_framework_context)


_agent_wrapper_async = _default_agent_wrapper_async
_agent_wrapper_sync = _default_agent_wrapper_sync


def trace_agent(func):
    """Annotation: @trace_agent

    Decorator to trace the agent invocation, add agent input and output to the monitor.
    """

    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        impl = globals().get('_agent_wrapper_async',
                             _default_agent_wrapper_async)
        return await impl(func, *args, **kwargs)

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        impl = globals().get('_agent_wrapper_sync',
                             _default_agent_wrapper_sync)
        return impl(func, *args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


# trace tool
def _handle_tool_result(start_info, source, result, pair_id):
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


def _process_tool(source, tool_input, start_info, pair_id):
    """Process common tool logic

    Args:
        source: The source/name of the tool
        tool_input: Input parameters for the tool
        start_info: Information about where the tool was called from
        pair_id: The ID for this tool invocation

    Returns:
        tuple: (self tool instance, updated source name)
    """
    ConversationMemoryModule().add_tool_input_info(start_info, source, tool_input, pair_id)


def _get_tool_info(func, *args, **kwargs):

    tool_input = _get_input(func, *args, **kwargs)
    source = func.__qualname__
    start_info = get_caller_info()
    pair_id = f"tool_{uuid.uuid4().hex}"
    self = tool_input.pop('self', None)
    if isinstance(self, object):
        name = getattr(self, 'name', None)
        if name is not None:
            source = name
    return self, source, tool_input, start_info, pair_id


async def _default_tool_wrapper_async(func, *args, **kwargs):
    # Extract tool input from arguments
    tool_instance, source, tool_input, start_info, pair_id = _get_tool_info(
        func, *args, **kwargs)
    with InvocationChainContext(source=source, node_type='tool'):
        _process_tool(source, tool_input, start_info, pair_id)
        result = await func(*args, **kwargs)
        return _handle_tool_result(start_info, source, result, pair_id)


def _default_tool_wrapper_sync(func, *args, **kwargs):
    # Extract tool input from arguments
    tool_instance, source, tool_input, start_info, pair_id = _get_tool_info(
        func, *args, **kwargs)
    with InvocationChainContext(source=source, node_type='tool'):
        _process_tool(source, tool_input, start_info, pair_id)
        result = func(*args, **kwargs)
        return _handle_tool_result(start_info, source, result, pair_id)


_tool_wrapper_async = _default_tool_wrapper_async
_tool_wrapper_sync = _default_tool_wrapper_sync


def trace_tool(func):
    """Annotation: @trace_tool

    A decorator to trace tool invocations, supporting both synchronous and asynchronous functions.
    It monitors tool execution, tracks timing, and maintains an invocation chain.
    """
    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        impl = globals().get('_tool_wrapper_async',
                             _default_tool_wrapper_async)
        return await impl(func, *args, **kwargs)


    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        impl = globals().get('_tool_wrapper_sync',
                             _default_tool_wrapper_sync)
        return impl(func, *args, **kwargs)

    return wrapper_async if asyncio.iscoroutinefunction(func) else wrapper_sync


# trace knowledge

def _process_knowledge(source, knowledge_input, start_info, pair_id):
    """Process common knowledge logic

    Args:
        source: The source/name of the knowledge
        knowledge_input: Input parameters for the knowledge
        start_info: Information about where the knowledge was called from
        pair_id: The ID for this knowledge invocation

    Returns:
        tuple: (self knowledge instance, updated source name)
    """
    ConversationMemoryModule().add_knowledge_input_info(start_info, source, knowledge_input, pair_id)


def _handle_knowledge_result(start_info, source, result, pair_id):
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


def _get_knowledge_info(func, *args, **kwargs):
    knowledge_input = _get_input(func, *args, **kwargs)
    source = func.__qualname__
    start_info = get_caller_info()
    pair_id = f"knowledge_{uuid.uuid4().hex}"
    self = knowledge_input.pop('self', None)
    if isinstance(self, object):
        name = getattr(self, 'name', None)
        if name is not None:
            source = name
    return self, source, knowledge_input, start_info, pair_id


async def _default_knowledge_wrapper_async(func, *args, **kwargs):
    # Get knowledge input from arguments
    knowledge_instance, source, knowledge_input, start_info, pair_id = _get_knowledge_info(
        func, *args, **kwargs)
    with InvocationChainContext(source=source, node_type='knowledge'):
        _process_knowledge(source, knowledge_input, start_info, pair_id)

        result = await func(*args, **kwargs)
        return _handle_knowledge_result(start_info, source, result,
                                        pair_id)


def _default_knowledge_wrapper_sync(func, *args, **kwargs):
    # Get knowledge input from arguments
    knowledge_instance, source, knowledge_input, start_info, pair_id = _get_knowledge_info(
        func, *args, **kwargs)
    with InvocationChainContext(source=source, node_type='knowledge'):
        _process_knowledge(source, knowledge_input, start_info, pair_id)

        result = func(*args, **kwargs)
        return _handle_knowledge_result(start_info, source, result, pair_id)


_knowledge_wrapper_async = _default_knowledge_wrapper_async
_knowledge_wrapper_sync = _default_knowledge_wrapper_sync


def trace_knowledge(func):
    """Annotation: @trace_knowledge

    Decorator to trace the knowledge invocation.
    """
    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        impl = globals().get('_knowledge_wrapper_async',
                             _default_knowledge_wrapper_async)
        return await impl(func, *args, **kwargs)

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        impl = globals().get('_knowledge_wrapper_sync',
                             _default_knowledge_wrapper_sync)
        return impl(func, *args, **kwargs)

    return wrapper_async if asyncio.iscoroutinefunction(func) else wrapper_sync
