# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Regression tests for Memory.get_with_context_budget budget selection.

The docstring promises the most recent messages survive budget pressure,
but the context-manager branch walked forward and broke at the first
overflow, silently keeping the OLDEST messages and dropping the newest.
"""
from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


class _FakeContextManager:
    def __init__(self, segments):
        self._segments = segments

    def get_context(self, session_id, context_type=None, limit=None, **kwargs):
        return self._segments


@pytest.fixture(autouse=True)
def _app_config():
    ApplicationConfigManager().app_configer = AppConfiger()


def _segment(content, role="user"):
    return SimpleNamespace(
        content=content,
        metadata=SimpleNamespace(extra_data={"role": role}),
    )


@pytest.fixture()
def patch_context_manager(monkeypatch):
    def _install(segments):
        fake = _FakeContextManager(segments)
        monkeypatch.setattr(
            ContextManagerManager, "get_instance_obj", lambda self, name: fake
        )
    return _install


def _make_memory() -> Memory:
    return Memory(context_manager_name="test_cm")


def test_budget_keeps_most_recent_messages(patch_context_manager):
    # get_memory_tokens with no LLM falls back to the character length of
    # the formatted message, so short contents give small counts.
    old, middle, recent = "a" * 10, "b" * 10, "c" * 10
    patch_context_manager([_segment(old), _segment(middle), _segment(recent)])
    memory = _make_memory()

    # A budget that fits exactly two messages: most-recent-first keeps
    # [middle, recent]; the broken forward walk kept [old, middle].
    budget = _budget_for_two(memory, [old, middle, recent])

    result = memory.get_with_context_budget("session", "agent", budget)
    contents = [m.content for m in result]
    assert contents == [middle, recent]


def test_budget_exhausted_by_huge_recent_returns_empty(patch_context_manager):
    patch_context_manager([_segment("a" * 10), _segment("b" * 5000)])
    memory = _make_memory()
    # The newest message alone exceeds the budget; the fallback branch
    # (and now this branch) returns an empty selection instead of the
    # oldest leftovers.
    result = memory.get_with_context_budget("session", "agent", 10)
    assert result == []


def _budget_for_two(memory, contents):
    """Budget that fits exactly the two most recent of three equal-size
    messages, measured the same way get_memory_tokens measures them."""
    from agentuniverse.base.util.memory_util import get_memory_tokens

    tokens = [get_memory_tokens([Message(content=c, type="user")], None)
              for c in contents]
    return tokens[1] + tokens[2]
