# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_workflow_dto.py

"""Unit tests for the WorkflowDTO."""

from agentuniverse_product.service.model.workflow_dto import WorkflowDTO


class TestWorkflowDTO:
    """Test WorkflowDTO model defaults and construction."""

    def test_defaults(self):
        dto = WorkflowDTO()
        assert dto.id is None
        assert dto.name == ""
        assert dto.description == ""
        assert dto.graph is None

    def test_full_construction(self):
        graph = {"nodes": ["a"], "edges": []}
        dto = WorkflowDTO(id="wf1", name="workflow", description="desc",
                          graph=graph)
        assert dto.id == "wf1"
        assert dto.name == "workflow"
        assert dto.description == "desc"
        assert dto.graph == graph

    def test_equality(self):
        assert WorkflowDTO(id="wf1") == WorkflowDTO(id="wf1")
        assert WorkflowDTO(id="wf1") != WorkflowDTO(id="wf2")
