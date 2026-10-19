# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_workflow_configer.py

"""Unit tests for the WorkflowConfiger."""

from types import SimpleNamespace

from agentuniverse.base.config.component_configer.configers.workflow_configer import \
    WorkflowConfiger


class TestWorkflowConfiger:
    """Test workflow configuration loading."""

    def test_defaults(self):
        configer = WorkflowConfiger()
        assert configer.id is None
        assert configer.name is None
        assert configer.description is None
        assert configer.graph is None

    def test_load_by_configer(self):
        configer = WorkflowConfiger()
        value = {"id": "wf1", "name": "workflow", "description": "desc",
                 "graph": {"nodes": []},
                 "metadata": {"type": "workflow", "module": "m",
                              "class": "C"}}
        returned = configer.load_by_configer(SimpleNamespace(value=value,
                                                             path="x.yaml"))
        assert returned is configer
        assert configer.id == "wf1"
        assert configer.name == "workflow"
        assert configer.description == "desc"
        assert configer.graph == {"nodes": []}
