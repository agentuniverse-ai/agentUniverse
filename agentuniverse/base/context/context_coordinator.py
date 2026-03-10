from dataclasses import dataclass
from typing import Any, Optional

import opentracing
from opentelemetry import context as otel_context
from opentelemetry.context import Context

from agentuniverse.base.context.framework_context_manager import \
    FrameworkContextManager
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager


# @Time    : 2025/4/15 15:35
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: context_coordinator.py


@dataclass
class ContextPack:
    """A snapshot bundle of runtime contexts for safe save/restore.

    Attributes:
        framework_context: A deep copy (or mapping) of framework-level variables.
        trace_context: Internal trace context from AuTraceManager.
        mcp_session: Saved MCP session info (session dict reference only).
        opentracing_span: The active OpenTracing span to be restored if present.
        otel_context: OpenTelemetry context object to attach on restore.
    """
    framework_context: dict
    trace_context: Any
    mcp_session: dict
    opentracing_span: Any
    otel_context: Optional[Context] = None


class ContextCoordinator:
    """Coordinates capture and restoration of multiple kinds of context.

    Use this helper to:
    - Save the current FrameworkContextManager variables, tracing info,
      and MCP session references into a single `ContextPack`.
    - Recover them later in another thread/task scope.

    Note: MCP session recovery only transfers the session dict reference
    (for using existing sessions). The ManagedExitStack lifecycle is
    owned by the request creator and is NOT transferred.
    """
    @classmethod
    def save_context(cls) -> ContextPack:
        """Capture a unified snapshot of the current runtime contexts.

        The returned ContextPack can be passed across thread boundaries
        and later fed into `recover_context()` to restore state.

        Returns:
            ContextPack: A bundle including framework, tracing, MCP, and OTEL contexts.
        """
        context_pack = ContextPack(
            framework_context=FrameworkContextManager().get_all_contexts(),
            trace_context=AuTraceManager().trace_context,
            mcp_session=MCPSessionManager().save_mcp_session(),
            opentracing_span=opentracing.tracer.active_span,
            otel_context=otel_context.get_current()
        )

        return context_pack

    @classmethod
    def recover_context(cls, context_pack: ContextPack):
        """Restore previously captured runtime contexts in a sub-thread.

        This method restores framework variables, tracing context, and MCP
        session references. It re-activates OpenTracing and OpenTelemetry
        contexts if available.

        Note: The sub-thread gets read access to MCP sessions but does not
        own the ManagedExitStack. It should NOT call close_session().

        Args:
            context_pack: The snapshot previously created by `save_context()`.

        Returns:
            Any: An OTEL context token if an OTEL context was attached; otherwise None.
        """
        for var_name, var_value in context_pack.framework_context.items():
            FrameworkContextManager().set_context(var_name, var_value)
        AuTraceManager().recover_trace(context_pack.trace_context)
        MCPSessionManager().recover_mcp_session(**context_pack.mcp_session)
        if context_pack.opentracing_span:
            opentracing.tracer.scope_manager.activate(
                context_pack.opentracing_span, finish_on_close=False
            )

        if context_pack.otel_context:
            token = otel_context.attach(context_pack.otel_context)
            return token

        return None

    @classmethod
    def end_context(cls):
        """Detach context references and clean up non-owned resources.

        For MCP sessions, this only detaches the ContextVar references
        without closing connections. The ManagedExitStack is closed
        separately by the request owner (e.g., in Flask's teardown_request
        or an async framework's middleware).
        """
        FrameworkContextManager().clear_all_contexts()
        AuTraceManager().reset_trace()
        MCPSessionManager().detach_session()
