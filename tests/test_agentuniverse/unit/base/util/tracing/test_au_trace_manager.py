# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_au_trace_manager.py
"""Unit tests for the deprecated base.util.tracing.au_trace_manager shim."""

import pytest

import agentuniverse.base.tracing.au_trace_manager as new_module
import agentuniverse.base.util.tracing.au_trace_manager as shim


class TestAuTraceManagerShim:
    """Test the deprecation shim re-exporting base.tracing.au_trace_manager."""

    def test_reexports_known_attribute(self):
        """Accessing a known attribute returns the real object from the new module."""
        assert shim.AuTraceManager is new_module.AuTraceManager

    def test_access_emits_deprecation_warning(self):
        """Accessing a re-exported attribute emits a DeprecationWarning."""
        with pytest.warns(DeprecationWarning):
            shim.set_session_id
        assert shim.set_session_id is new_module.set_session_id

    def test_unknown_attribute_raises(self):
        """An attribute missing from the new module raises AttributeError."""
        with pytest.raises(AttributeError):
            shim.this_name_does_not_exist

    def test_all_matches_new_module(self):
        """The shim __all__ mirrors the new module's __all__."""
        assert shim.__all__ == getattr(new_module, "__all__", [])

    def test_function_delegation(self):
        """Re-exported callables behave like the new module's functions."""
        shim.set_session_id("shim-sess")
        assert new_module.get_session_id() == "shim-sess"
