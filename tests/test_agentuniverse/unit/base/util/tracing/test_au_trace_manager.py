# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_au_trace_manager.py

"""Unit tests for the deprecated tracing module re-export shim."""

import importlib

import pytest

old = importlib.import_module(
    "agentuniverse.base.util.tracing.au_trace_manager")
new = importlib.import_module(
    "agentuniverse.base.tracing.au_trace_manager")


class TestAuTraceManagerShim:
    """Test the deprecation shim re-exporting the new module."""

    def test_known_attribute_forwarded_with_warning(self):
        for name in ["AuTraceManager", "AuTraceContext"]:
            if not hasattr(new, name):
                continue
            with pytest.warns(DeprecationWarning):
                value = getattr(old, name)
            assert value is getattr(new, name)

    def test_all_matches_new_module(self):
        assert old.__all__ == getattr(new, "__all__", [])

    def test_unknown_attribute_raises(self):
        with pytest.raises(AttributeError):
            getattr(old, "DefinitelyNotASymbol")
