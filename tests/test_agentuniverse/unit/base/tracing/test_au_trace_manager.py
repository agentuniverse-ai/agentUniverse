# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for the AuTraceManager trace manager and its helpers.

AuTraceManager keeps the active AuTraceContext in a context variable and
exposes typed setters/getters plus module-level convenience functions.  The
tests below exercise deterministic set/get round-trips and reset behavior
without relying on any live tracing infrastructure.
"""

import pytest

from agentuniverse.base.tracing.au_trace_manager import AuTraceManager
from agentuniverse.base.tracing import au_trace_manager as module_api


@pytest.fixture
def manager():
    """A clean manager instance reset before every test."""
    instance = AuTraceManager()
    instance.reset_trace()
    return instance


class TestManagerRoundTrips:
    """Tests for the manager's session/trace/span accessors."""

    def test_fresh_session_id_is_none(self, manager):
        assert manager.get_session_id() is None

    def test_set_and_get_session_id(self, manager):
        manager.set_session_id("sess-alpha")
        assert manager.get_session_id() == "sess-alpha"

    def test_set_and_get_trace_id(self, manager):
        manager.set_trace_id("1" * 32)
        assert manager.get_trace_id() == "1" * 32

    def test_set_and_get_span_id(self, manager):
        manager.set_span_id("2" * 16)
        assert manager.get_span_id() == "2" * 16

    def test_reset_trace_clears_session(self, manager):
        manager.set_session_id("sess-beta")
        manager.reset_trace()
        assert manager.get_session_id() is None


class TestTraceDict:
    """Tests for building the trace dictionary."""

    def test_trace_dict_omits_unset_session(self, manager):
        trace_dict = manager.get_trace_dict()
        assert "session_id" not in trace_dict
        assert "trace_id" in trace_dict
        assert "span_id" in trace_dict

    def test_trace_dict_reflects_set_fields(self, manager):
        manager.set_session_id("sess-gamma")
        manager.set_trace_id("3" * 32)
        manager.set_span_id("4" * 16)
        assert manager.get_trace_dict() == {
            "session_id": "sess-gamma",
            "trace_id": "3" * 32,
            "span_id": "4" * 16,
        }


class TestModuleLevelFunctions:
    """Tests for the module-level convenience wrappers."""

    def test_module_session_functions_round_trip(self, manager):
        module_api.set_session_id("sess-delta")
        assert module_api.get_session_id() == "sess-delta"

    def test_module_trace_id_functions_round_trip(self, manager):
        module_api.set_trace_id("5" * 32)
        assert module_api.get_trace_id() == "5" * 32

    def test_module_span_id_functions_round_trip(self, manager):
        module_api.set_span_id("6" * 16)
        assert module_api.get_span_id() == "6" * 16

    def test_module_get_trace_dict_matches_manager(self, manager):
        module_api.set_session_id("sess-epsilon")
        assert module_api.get_trace_dict()["session_id"] == "sess-epsilon"


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
