# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_workflow_manager.py
"""Unit tests for WorkflowManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.workflow.workflow import Workflow
from agentuniverse.workflow.workflow_manager import WorkflowManager


class TestWorkflowManager:
    def test_singleton(self):
        assert WorkflowManager() is WorkflowManager()

    def test_component_type_is_workflow(self):
        assert WorkflowManager()._component_type == ComponentEnum.WORKFLOW

    def test_register_and_unregister(self):
        manager = WorkflowManager()
        workflow = Workflow(id='wf_reg')
        manager.register('test_wf_191', workflow)
        try:
            assert 'test_wf_191' in manager.get_instance_name_list()
            assert manager._instance_obj_map['test_wf_191'] is workflow
        finally:
            manager.unregister('test_wf_191')
        assert 'test_wf_191' not in manager.get_instance_name_list()

    def test_unregister_unknown_is_safe(self):
        WorkflowManager().unregister('definitely_not_registered')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
