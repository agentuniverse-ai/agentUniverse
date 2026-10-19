# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for agentuniverse.base.annotation.singleton."""
from agentuniverse.base.annotation.singleton import singleton


@singleton
class _Single:
    def __init__(self, value: int = 1):
        self.value = value


class TestSingleton:
    """Tests for the singleton class decorator."""

    def test_returns_same_instance(self):
        first = _Single()
        second = _Single()
        assert first is second

    def test_constructor_runs_once(self):
        calls = []

        @singleton
        class _Counted:
            def __init__(self):
                calls.append(1)

        _Counted()
        _Counted()
        assert len(calls) == 1

    def test_wrapper_preserves_class_name(self):
        assert _Single.__name__ == "_Single"

    def test_wrapper_is_callable(self):
        assert callable(_Single)

    def test_independent_singletons_do_not_share_instances(self):
        @singleton
        class _Other:
            pass

        assert _Other() is not _Single()

    def test_first_call_arguments_are_used(self):
        @singleton
        class _WithValue:
            def __init__(self, value: int = 1):
                self.value = value

        assert _WithValue(value=42).value == 42
        assert _WithValue(value=0).value == 42
