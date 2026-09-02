# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_au_trace_manager.py
"""Unit tests for AuTraceManager."""

import pytest

import agentuniverse.base.tracing.au_trace_manager as au_trace_manager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager
from agentuniverse.base.tracing.au_trace_context import AuTraceContext


class TestAuTraceManager:
    """Test AuTraceManager context management and id round-tripping."""

    def test_singleton_identity(self):
        """The singleton decorator returns the same manager instance."""
        assert AuTraceManager() is AuTraceManager()

    def test_trace_context_creates_and_caches_context(self):
        """trace_context creates a context once and caches it in the ContextVar."""
        manager = AuTraceManager()
        first = manager.trace_context
        second = manager.trace_context
        assert isinstance(first, AuTraceContext)
        assert first is second
        assert first.trace_id is not None
        assert first.span_id is not None

    def test_reset_trace_replaces_context(self):
        """reset_trace clears the ContextVar so a fresh context is created."""
        manager = AuTraceManager()
        old = manager.trace_context
        manager.reset_trace()
        new = manager.trace_context
        assert new is not old
        assert new.trace_id is not None

    def test_recover_trace_restores_context(self):
        """recover_trace installs an existing context into the ContextVar."""
        manager = AuTraceManager()
        restored = AuTraceContext.new_context()
        manager.recover_trace(restored)
        assert manager.trace_context is restored

    def test_id_round_trip(self):
        """session/trace/span id setters and getters round-trip values."""
        manager = AuTraceManager()
        ctx = AuTraceContext.new_context()
        ctx.set_session_id("sess-1")
        ctx.set_trace_id("trace-1")
        ctx.set_span_id("span-1")
        manager.recover_trace(ctx)
        assert manager.get_session_id() == "sess-1"
        assert manager.get_trace_id() == "trace-1"
        assert manager.get_span_id() == "span-1"

    def test_get_trace_dict_only_includes_set_ids(self):
        """get_trace_dict includes only non-empty session/trace/span ids."""
        manager = AuTraceManager()
        fresh = AuTraceContext.new_context()
        manager.recover_trace(fresh)
        assert fresh.session_id is None
        d = manager.get_trace_dict()
        assert "session_id" not in d
        assert d["trace_id"] is not None
        assert d["span_id"] is not None
        fresh.set_session_id("s")
        assert "session_id" in manager.get_trace_dict()

    def test_module_level_helpers(self):
        """Module-level helpers delegate to the singleton manager."""
        au_trace_manager.set_session_id("helper-sess")
        assert au_trace_manager.get_session_id() == "helper-sess"
        d = au_trace_manager.get_trace_dict()
        assert d.get("session_id") == "helper-sess"
        assert "trace_id" in d
