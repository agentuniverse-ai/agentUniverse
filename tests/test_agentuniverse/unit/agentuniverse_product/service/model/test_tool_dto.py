# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_dto.py

"""Unit tests for the ToolDTO."""

import pytest

from agentuniverse_product.service.model.tool_dto import ToolDTO


class TestToolDTO:
    """Test ToolDTO model defaults and construction."""

    def test_defaults(self):
        dto = ToolDTO(id="t1")
        assert dto.nickname == ""
        assert dto.avatar == ""
        assert dto.description == ""
        assert dto.parameters == []
        assert dto.openapi_schema == {}

    def test_full_construction(self):
        dto = ToolDTO(id="t1", nickname="tool", description="call api",
                      parameters=["q"], openapi_schema={"url": "x"})
        assert dto.nickname == "tool"
        assert dto.parameters == ["q"]
        assert dto.openapi_schema == {"url": "x"}

    def test_id_is_required(self):
        with pytest.raises(Exception):
            ToolDTO()

    def test_parameters_not_shared_between_instances(self):
        first = ToolDTO(id="t1")
        first.parameters.append("extra")
        assert ToolDTO(id="t2").parameters == []
