# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08
# @Author  : Yue Wang
# @FileName: test_llm_dto.py
"""Unit tests for the LlmDTO pydantic model."""

import pytest
from pydantic import ValidationError

from agentuniverse_product.service.model.llm_dto import LlmDTO


class TestLlmDTO:
    """Test LlmDTO field defaults, validation and serialization."""

    @pytest.fixture
    def llm_dto(self) -> LlmDTO:
        """Return a fully populated LlmDTO instance."""
        return LlmDTO(
            id="llm-1",
            nickname="chat",
            temperature=0.7,
            model_name=["gpt-4", "gpt-4-turbo"],
        )

    def test_default_values(self):
        """Optional fields fall back to their declared defaults."""
        dto = LlmDTO(id="llm-0")
        assert dto.id == "llm-0"
        assert dto.nickname == ""
        assert dto.temperature is None
        assert dto.model_name == []

    def test_explicit_values_stored(self, llm_dto):
        """Explicitly provided constructor values are preserved."""
        assert llm_dto.nickname == "chat"
        assert llm_dto.temperature == 0.7
        assert llm_dto.model_name == ["gpt-4", "gpt-4-turbo"]

    def test_id_is_required(self):
        """Creating an LlmDTO without an id raises a validation error."""
        with pytest.raises(ValidationError):
            LlmDTO()

    def test_temperature_accepts_int(self):
        """A float field also accepts an integer literal value."""
        dto = LlmDTO(id="llm-2", temperature=1)
        assert dto.temperature == 1.0

    def test_model_dump_round_trip(self, llm_dto):
        """model_dump returns a plain dict reconstructing an equal model."""
        data = llm_dto.model_dump()
        assert data["id"] == "llm-1"
        assert data["nickname"] == "chat"
        assert LlmDTO(**data) == llm_dto

    def test_model_name_accepts_single_value(self):
        """model_name keeps a one-element list intact."""
        dto = LlmDTO(id="llm-3", model_name=["deepseek-chat"])
        assert dto.model_name == ["deepseek-chat"]
