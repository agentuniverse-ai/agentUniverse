from types import SimpleNamespace

import pytest

from agentuniverse.base.context import context_coordinator as coordinator_module


class NoOpContextManager:
    def recover_trace(self, trace_context):
        pass

    def recover_mcp_session(self, **session):
        pass


class RecordingScope:
    def __init__(self):
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def test_recovered_context_closes_both_tracing_resources(monkeypatch):
    scope = RecordingScope()
    otel_token = object()
    detached_tokens = []

    monkeypatch.setattr(
        coordinator_module,
        "AuTraceManager",
        lambda: NoOpContextManager(),
    )
    monkeypatch.setattr(
        coordinator_module,
        "MCPSessionManager",
        lambda: NoOpContextManager(),
    )
    monkeypatch.setattr(
        coordinator_module,
        "opentracing",
        SimpleNamespace(
            tracer=SimpleNamespace(
                scope_manager=SimpleNamespace(activate=lambda *args, **kwargs: scope)
            )
        ),
    )
    monkeypatch.setattr(
        coordinator_module,
        "otel_context",
        SimpleNamespace(
            attach=lambda context: otel_token,
            detach=detached_tokens.append,
        ),
    )

    recovered_context = coordinator_module.ContextCoordinator.recover_context(
        coordinator_module.ContextPack({}, None, {}, object(), object())
    )
    recovered_context.close()

    assert scope.close_calls == 1
    assert detached_tokens == [otel_token]


def test_recovered_context_closes_opentracing_scope_when_otel_detach_fails(
    monkeypatch,
):
    scope = RecordingScope()

    def fail_to_detach(token):
        raise RuntimeError("detach failed")

    monkeypatch.setattr(coordinator_module.otel_context, "detach", fail_to_detach)
    recovered_context = coordinator_module.RecoveredContext(scope, object())

    with pytest.raises(RuntimeError, match="detach failed"):
        recovered_context.close()

    assert scope.close_calls == 1


def test_recover_context_closes_scope_when_otel_attach_fails(monkeypatch):
    scope = RecordingScope()

    monkeypatch.setattr(
        coordinator_module,
        "AuTraceManager",
        lambda: NoOpContextManager(),
    )
    monkeypatch.setattr(
        coordinator_module,
        "MCPSessionManager",
        lambda: NoOpContextManager(),
    )
    monkeypatch.setattr(
        coordinator_module,
        "opentracing",
        SimpleNamespace(
            tracer=SimpleNamespace(
                scope_manager=SimpleNamespace(activate=lambda *args, **kwargs: scope)
            )
        ),
    )

    def fail_to_attach(context):
        raise RuntimeError("attach failed")

    monkeypatch.setattr(
        coordinator_module,
        "otel_context",
        SimpleNamespace(attach=fail_to_attach),
    )

    with pytest.raises(RuntimeError, match="attach failed"):
        coordinator_module.ContextCoordinator.recover_context(
            coordinator_module.ContextPack({}, None, {}, object(), object())
        )

    assert scope.close_calls == 1
