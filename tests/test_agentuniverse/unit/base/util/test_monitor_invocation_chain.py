from unittest.mock import patch

from agentuniverse.base.util.monitor.monitor import Monitor


def test_invocation_chain_reads_are_empty_without_active_trace():
    with patch(
        "agentuniverse.base.util.monitor.monitor.AuTraceManager"
    ) as trace_manager:
        trace_manager.return_value.get_trace_id.return_value = None
        assert Monitor.get_invocation_chain() == []
        assert Monitor.get_invocation_chain_bak() == []


def test_invocation_chain_reads_context_when_trace_is_active():
    with patch(
        "agentuniverse.base.util.monitor.monitor.AuTraceManager"
    ) as trace_manager:
        trace_manager.return_value.get_trace_id.return_value = "trace-1"
        with patch(
            "agentuniverse.base.util.monitor.monitor.FrameworkContextManager"
        ) as context_manager:
            context_manager.return_value.get_context.side_effect = [
                [{"source": "agent"}],
                [{"source": "tool"}],
            ]
            assert Monitor.get_invocation_chain() == [{"source": "agent"}]
            assert Monitor.get_invocation_chain_bak() == [{"source": "tool"}]
