# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the deprecation shim agentuniverse.base.util.tracing.au_trace_context."""

import warnings

import pytest

import agentuniverse.base.tracing.au_trace_context as new_module
import agentuniverse.base.util.tracing.au_trace_context as shim


class TestDeprecationShim:
    """Tests for the module-level __getattr__ forwarding."""

    def test_forwarded_attribute_matches_new_module(self):
        assert shim.AuTraceContext is new_module.AuTraceContext

    def test_access_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            shim.AuTraceContext
        assert any(issubclass(item.category, DeprecationWarning) for item in caught)

    def test_warning_message_points_to_new_module(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            shim.AuTraceContext
        assert any(
            "agentuniverse.base.tracing.au_trace_context" in str(item.message)
            for item in caught
        )

    def test_unknown_attribute_raises_attribute_error(self):
        with pytest.raises(AttributeError):
            shim.no_such_symbol_xyz

    def test_all_matches_new_module(self):
        assert shim.__all__ == getattr(new_module, "__all__", [])
