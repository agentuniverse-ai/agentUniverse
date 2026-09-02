# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_workflow_configer.py
"""Unit tests for WorkflowConfiger configuration parsing."""

import pytest

from agentuniverse.base.config.component_configer.configers.workflow_configer import (
    WorkflowConfiger,
)
from agentuniverse.base.config.configer import Configer


class TestWorkflowConfiger:
    """Test WorkflowConfiger field parsing from a Configer."""

    @pytest.fixture
    def configer(self):
        """Build a Configer holding a workflow configuration."""
        configer = Configer()
        configer.value = {
            "id": "wf_1",
            "name": "demo_workflow",
            "description": "a tiny workflow",
            "graph": {"nodes": ["start", "end"], "edges": [["start", "end"]]},
        }
        return configer

    def test_defaults_before_load(self):
        """All parsed properties are None before load runs."""
        configer = WorkflowConfiger(Configer())
        assert configer.id is None
        assert configer.name is None
        assert configer.graph is None

    def test_load_parses_all_fields(self, configer):
        """load maps id, name, description and graph onto its properties."""
        configer = WorkflowConfiger(configer).load()
        assert configer.id == "wf_1"
        assert configer.name == "demo_workflow"
        assert configer.description == "a tiny workflow"
        assert configer.graph == {"nodes": ["start", "end"], "edges": [["start", "end"]]}

    def test_load_returns_self(self, configer):
        """load is fluent and returns the same configer object."""
        configer = WorkflowConfiger(configer)
        assert configer.load() is configer

    def test_load_wraps_parse_failure(self):
        """A non-dict configer value raises a wrapped parse error."""
        bad_configer = Configer()
        bad_configer.value = ["not", "a", "dict"]
        with pytest.raises(Exception, match="Failed to parse the component configuration"):
            WorkflowConfiger(bad_configer).load()

    def test_missing_keys_stay_none(self):
        """Keys absent from the config keep their None default."""
        partial = Configer()
        partial.value = {"id": "only_id"}
        configer = WorkflowConfiger(partial).load()
        assert configer.id == "only_id"
        assert configer.name is None
        assert configer.description is None
        assert configer.graph is None
