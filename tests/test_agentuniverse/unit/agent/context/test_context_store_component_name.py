# !/usr/bin/env python3
# -*- coding:utf-8 -*-
"""The context store must expose the component name the base class reads."""

import pytest

from agentuniverse.agent.context.context_store import ContextStore
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_context_store_declares_component_name():
    assert "name" in ContextStore.model_fields


def test_ram_context_store_keeps_component_name():
    store = RamContextStore(name="test_ram_store", max_segments=10, ttl_hours=1)

    assert store.name == "test_ram_store"
    assert store.max_segments == 10
    assert store.ttl_hours == 1


def test_ram_context_store_defaults_component_name():
    assert RamContextStore().name == ""
