# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01 10:00
# @Author  : Yue Wang
# @FileName: test_context_coordinator.py
"""Unit tests for ContextCoordinator."""

import pytest
from opentelemetry import context as otel_context

from agentuniverse.base.context.context_coordinator import (
    ContextCoordinator,
    ContextPack,
)
from agentuniverse.base.context.framework_context_manager import (
    FrameworkContextManager,
)


class TestContextCoordinator:
    """Test suite for ContextCoordinator."""

    @pytest.fixture(autouse=True)
    def clean_contexts(self):
        FrameworkContextManager().clear_all_contexts()
        yield
        FrameworkContextManager().clear_all_contexts()

    def test_save_context_returns_context_pack(self):
        pack = ContextCoordinator.save_context()

        assert isinstance(pack, ContextPack)
        assert isinstance(pack.framework_context, dict)
        assert isinstance(pack.mcp_session, dict)
        assert set(pack.mcp_session.keys()) == {'mcp_session_dict', 'exit_stack'}
        assert pack.trace_context is not None

    def test_recover_context_restores_framework_values(self):
        fcm = FrameworkContextManager()
        fcm.set_context('user_id', 'alice')
        pack = ContextCoordinator.save_context()

        fcm.clear_all_contexts()
        assert fcm.get_all_contexts() == {}

        ContextCoordinator.recover_context(pack)
        assert fcm.get_context('user_id') == 'alice'

    def test_recover_returns_none_without_otel_context(self):
        pack = ContextPack(
            framework_context={},
            trace_context=None,
            mcp_session={'mcp_session_dict': None, 'exit_stack': None},
            opentracing_span=None,
            otel_context=None,
        )
        assert ContextCoordinator.recover_context(pack) is None

    def test_recover_attaches_non_empty_otel_context(self):
        non_empty = otel_context.set_value('test_key', 'test_value')
        pack = ContextPack(
            framework_context={},
            trace_context=None,
            mcp_session={'mcp_session_dict': None, 'exit_stack': None},
            opentracing_span=None,
            otel_context=non_empty,
        )
        token = ContextCoordinator.recover_context(pack)
        try:
            assert token is not None
        finally:
            otel_context.detach(token)

    def test_end_context_clears_framework_context(self):
        fcm = FrameworkContextManager()
        fcm.set_context('user_id', 'bob')
        assert fcm.get_context('user_id') == 'bob'

        ContextCoordinator.end_context()
        assert fcm.get_all_contexts() == {}

    def test_context_pack_otel_context_defaults_to_none(self):
        pack = ContextPack(
            framework_context={'a': 1},
            trace_context=None,
            mcp_session={},
            opentracing_span=None,
        )
        assert pack.otel_context is None
        assert pack.framework_context == {'a': 1}
