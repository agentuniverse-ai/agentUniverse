# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08
# @Author  : Yue Wang
# @FileName: test_plugin_dto.py
"""Unit tests for the PluginDTO pydantic model."""

import pytest
from pydantic import ValidationError

from agentuniverse_product.service.model.plugin_dto import PluginDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO


class TestPluginDTO:
    """Test PluginDTO field defaults, validation and serialization."""

    @pytest.fixture
    def plugin_dto(self) -> PluginDTO:
        """Return a fully populated PluginDTO instance."""
        return PluginDTO(
            id="plugin-1",
            nickname="search",
            avatar="/avatar/search.png",
            description="search tools",
            toolset=[{"id": "t1", "nickname": "tool-a"}],
            openapi_desc="{}",
        )

    def test_default_values(self):
        """Optional fields fall back to their declared defaults."""
        dto = PluginDTO(id="plugin-0")
        assert dto.nickname == ""
        assert dto.avatar == ""
        assert dto.description == ""
        assert dto.openapi_desc == ""
        assert dto.toolset == []

    def test_explicit_values_stored(self, plugin_dto):
        """Explicitly provided constructor values are preserved."""
        assert plugin_dto.nickname == "search"
        assert plugin_dto.avatar == "/avatar/search.png"
        assert plugin_dto.description == "search tools"
        assert plugin_dto.openapi_desc == "{}"

    def test_id_is_required(self):
        """Creating a PluginDTO without an id raises a validation error."""
        with pytest.raises(ValidationError):
            PluginDTO()

    def test_tool_dicts_coerced_to_tool_dto(self, plugin_dto):
        """Nested tool dicts are coerced into ToolDTO instances."""
        assert isinstance(plugin_dto.toolset[0], ToolDTO)
        assert plugin_dto.toolset[0].id == "t1"
        assert plugin_dto.toolset[0].nickname == "tool-a"

    def test_toolset_accepts_tool_dto_instances(self):
        """toolset also accepts already-built ToolDTO instances."""
        tool = ToolDTO(id="t2", nickname="tool-b")
        dto = PluginDTO(id="plugin-2", toolset=[tool])
        assert dto.toolset == [tool]

    def test_model_dump_round_trip(self, plugin_dto):
        """model_dump returns a plain dict reconstructing an equal model."""
        data = plugin_dto.model_dump()
        assert data["id"] == "plugin-1"
        assert data["toolset"][0]["id"] == "t1"
        assert PluginDTO(**data) == plugin_dto
