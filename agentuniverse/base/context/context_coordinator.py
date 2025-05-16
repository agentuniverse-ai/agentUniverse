# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from dataclasses import dataclass
from typing import Any

import opentracing
from agentuniverse.base.context.framework_context_manager import \
    FrameworkContextManager
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager
from agentuniverse.base.util.tracing.au_trace_manager import AuTraceManager


# @Time    : 2025/4/15 15:35
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: context_coordinator.py


@dataclass
class ContextPack:
    framework_context: dict
    trace_context: Any
    mcp_session: dict
    opentracing_span: Any


class ContextCoordinator:

    @classmethod
    def save_context(cls) -> ContextPack:
        context_pack = ContextPack(
            framework_context=FrameworkContextManager().get_all_contexts(),
            trace_context=AuTraceManager().trace_context,
            mcp_session=MCPSessionManager().save_mcp_session(),
            opentracing_span=opentracing.tracer.active_span
        )

        return context_pack

    @classmethod
    def recover_context(cls, context_pack: ContextPack):
        for var_name, var_value in context_pack.framework_context.items():
            FrameworkContextManager().set_context(var_name, var_value)
        AuTraceManager().recover_trace(context_pack.trace_context)
        MCPSessionManager().recover_mcp_session(**context_pack.mcp_session)
        if context_pack.opentracing_span:
            opentracing.tracer.scope_manager.activate(
                context_pack.opentracing_span, finish_on_close=False
            )

    @classmethod
    def end_context(cls):
        FrameworkContextManager().clear_all_contexts()
        AuTraceManager().reset_trace()
        MCPSessionManager().safe_close_stack()
