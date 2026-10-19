# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01 10:00
# @Author  : Yue Wang
# @FileName: test_framework_context_manager.py
"""Unit tests for FrameworkContextManager."""

import pytest

from agentuniverse.base.context.framework_context_manager import (
    FrameworkContextManager,
)


class TestFrameworkContextManager:
    """Test suite for FrameworkContextManager."""

    @pytest.fixture(autouse=True)
    def fresh_manager(self):
        manager = FrameworkContextManager()
        manager.clear_all_contexts()
        yield manager
        manager.clear_all_contexts()

    def test_context_dict_starts_empty(self, fresh_manager):
        assert fresh_manager.context_dict == {}

    def test_set_and_get_context(self, fresh_manager):
        token = fresh_manager.set_context('user_id', 'alice')

        assert token is not None
        assert fresh_manager.get_context('user_id') == 'alice'

    def test_get_context_returns_default_when_missing(self, fresh_manager):
        assert fresh_manager.get_context('missing') is None
        assert fresh_manager.get_context('missing', 'fallback') == 'fallback'

    def test_is_context_exist(self, fresh_manager):
        assert not fresh_manager.is_context_exist('user_id')

        fresh_manager.set_context('user_id', 'alice')
        assert fresh_manager.is_context_exist('user_id')

    def test_del_context_clears_value_and_force_removes_key(self, fresh_manager):
        fresh_manager.set_context('user_id', 'alice')

        fresh_manager.del_context('user_id')
        assert fresh_manager.is_context_exist('user_id')
        assert fresh_manager.get_context('user_id') is None

        fresh_manager.del_context('user_id', force=True)
        assert not fresh_manager.is_context_exist('user_id')

    def test_get_all_contexts_deep_copies_values(self, fresh_manager):
        fresh_manager.set_context('cfg', {'k': 1})
        fresh_manager.set_context('name', 'demo')

        all_contexts = fresh_manager.get_all_contexts()
        assert all_contexts == {'cfg': {'k': 1}, 'name': 'demo'}
        assert all_contexts['cfg'] is not fresh_manager.get_context('cfg')

    def test_set_all_contexts_returns_token_per_key(self, fresh_manager):
        tokens = fresh_manager.set_all_contexts({'a': 1, 'b': 'two'})

        assert set(tokens.keys()) == {'a', 'b'}
        assert fresh_manager.get_context('a') == 1
        assert fresh_manager.get_context('b') == 'two'

    def test_clear_all_contexts(self, fresh_manager):
        fresh_manager.set_context('user_id', 'alice')
        assert fresh_manager.get_context('user_id') == 'alice'

        fresh_manager.clear_all_contexts()
        assert fresh_manager.get_all_contexts() == {}

    def test_set_log_context_merges_into_log_context(self, fresh_manager):
        fresh_manager.set_context('LOG_CONTEXT', {'request_id': 'r-1'})

        fresh_manager.set_log_context('user_id', 'alice')
        assert fresh_manager.get_context('LOG_CONTEXT') == {
            'request_id': 'r-1',
            'user_id': 'alice',
        }
