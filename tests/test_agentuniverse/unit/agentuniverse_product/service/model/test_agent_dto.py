# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_dto.py

"""Unit tests for the AgentDTO."""

import pytest

from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.planner_dto import PlannerDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO


class TestAgentDTO:
    """Test AgentDTO model defaults, nesting and construction."""

    def test_defaults(self):
        dto = AgentDTO(id="a1")
        assert dto.nickname == ""
        assert dto.opening_speech == ""
        assert dto.prompt is None
        assert dto.llm is None
        assert dto.tool == []
        assert dto.memory == ""
        assert dto.planner is None
        assert dto.knowledge == []
        assert dto.mtime is None

    def test_id_is_required(self):
        with pytest.raises(Exception):
            AgentDTO()

    def test_nested_dtos_coerced(self):
        dto = AgentDTO(id="a1",
                       tool=[{"id": "t1"}],
                       knowledge=[{"id": "k1", "nickname": "kb"}],
                       planner={"id": "p1"})
        assert dto.tool == [ToolDTO(id="t1")]
        assert dto.knowledge == [KnowledgeDTO(id="k1", nickname="kb")]
        assert dto.planner == PlannerDTO(id="p1")

    def test_equality(self):
        assert AgentDTO(id="a1") == AgentDTO(id="a1")
        assert AgentDTO(id="a1") != AgentDTO(id="a2")
