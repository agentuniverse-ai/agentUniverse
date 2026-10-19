# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.component.application_component_manager."""

import pytest

from agentuniverse.base.component.application_component_manager import ApplicationComponentManager

_ATTR_PREFIX = "_ApplicationComponentManager__"


@pytest.fixture
def manager():
    """Return the ApplicationComponentManager singleton instance."""
    return ApplicationComponentManager()


class TestApplicationComponentManager:
    """Tests for the singleton ApplicationComponentManager."""

    def test_singleton_returns_same_instance(self, manager):
        assert ApplicationComponentManager() is manager

    def test_constructor_requires_no_arguments(self):
        ApplicationComponentManager()
        assert callable(ApplicationComponentManager)

    def test_wrapper_preserves_original_class_name(self):
        assert ApplicationComponentManager.__name__ == "ApplicationComponentManager"

    def test_instance_is_instance_of_wrapped_class(self):
        inner_class = ApplicationComponentManager.__wrapped__
        assert isinstance(ApplicationComponentManager(), inner_class)

    def test_initializes_agent_manager(self, manager):
        assert getattr(manager, f"{_ATTR_PREFIX}agent_manager") is not None

    def test_initializes_llm_manager(self, manager):
        assert getattr(manager, f"{_ATTR_PREFIX}llm_manager") is not None

    def test_initializes_planner_manager(self, manager):
        assert getattr(manager, f"{_ATTR_PREFIX}planner_manager") is not None

    def test_initializes_knowledge_and_tool_managers(self, manager):
        assert getattr(manager, f"{_ATTR_PREFIX}knowledge") is not None
        assert getattr(manager, f"{_ATTR_PREFIX}tool_manager") is not None
