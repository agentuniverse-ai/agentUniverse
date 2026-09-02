# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 13:25
# @Author  : yuewang
# @FileName: test_workflow_manager.py
"""Unit tests for WorkflowManager."""

import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.workflow.workflow_manager import WorkflowManager


class DummyWorkflow(ComponentBase):
    """Minimal workflow component for manager tests."""
    name: str = None
    component_type: ComponentEnum = ComponentEnum.WORKFLOW


@pytest.fixture
def manager():
    """Return the WorkflowManager singleton."""
    return WorkflowManager()


class TestWorkflowManager:
    """Test WorkflowManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is WorkflowManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.WORKFLOW

    def test_register_and_get(self, manager):
        wf = DummyWorkflow(name='wf1')
        manager.register('app.workflow.wf1', wf)
        assert manager.get_instance_obj('wf1', appname='app', new_instance=False) is wf

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_wf_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_wf_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.workflow.wf2', DummyWorkflow(name='wf2'))
        manager.unregister('app.workflow.wf2')
        assert manager.get_instance_obj('wf2', appname='app') is None
