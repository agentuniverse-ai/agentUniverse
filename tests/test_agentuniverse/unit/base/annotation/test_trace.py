import asyncio
import importlib

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


class _StubConversationMemoryModule:
    """ stubconversationmemorymodule.
    """
    def add_agent_input_info(self, *args, **kwargs):
        """Add agent input info.
        """
        pass

    def add_agent_result_info(self, *args, **kwargs):
        """Add agent result info.
        """
        pass


class _StubAgent:
    """ stubagent.
    """
    agent_model = None


async def _run_agent(self, **kwargs):
    """ run agent.
    """
    return "done"


def test_async_agent_wrapper_restores_parent_invocation_chain(monkeypatch):
    """Test that async agent wrapper restores parent invocation chain.
    """
    trace_module = importlib.import_module("agentuniverse.base.annotation.trace")
    monkeypatch.setattr(
        trace_module,
        "ConversationMemoryModule",
        _StubConversationMemoryModule,
    )

    async def run_in_parent_context():
        """Run in parent context.
        """
        context_manager = FrameworkContextManager()
        context_manager.clear_all_contexts()
        parent = {"source": "parent-agent", "type": "agent"}
        trace_module.Monitor.init_invocation_chain()
        trace_module.Monitor.add_invocation_chain(parent)

        try:
            result = await trace_module._default_agent_wrapper_async(
                _run_agent,
                _StubAgent(),
            )

            assert result == "done"
            assert trace_module.Monitor.get_invocation_chain() == [parent]
        finally:
            trace_module.Monitor.clear_invocation_chain()
            context_manager.clear_all_contexts()

    asyncio.run(run_in_parent_context())
