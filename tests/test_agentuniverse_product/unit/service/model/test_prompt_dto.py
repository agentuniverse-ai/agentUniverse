# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08
# @Author  : Yue Wang
# @FileName: test_prompt_dto.py
"""Unit tests for the PromptDTO pydantic model."""

import pytest

from agentuniverse_product.service.model.prompt_dto import PromptDTO


class TestPromptDTO:
    """Test PromptDTO field defaults, validation and serialization."""

    @pytest.fixture
    def prompt_dto(self) -> PromptDTO:
        """Return a fully populated PromptDTO instance."""
        return PromptDTO(
            introduction="You are a helpful assistant.",
            target="Answer user questions.",
            instruction="Be concise and accurate.",
        )

    def test_default_values(self):
        """All fields fall back to an empty string when not provided."""
        dto = PromptDTO()
        assert dto.introduction == ""
        assert dto.target == ""
        assert dto.instruction == ""

    def test_explicit_values_stored(self, prompt_dto):
        """Explicitly provided constructor values are preserved."""
        assert prompt_dto.introduction == "You are a helpful assistant."
        assert prompt_dto.target == "Answer user questions."
        assert prompt_dto.instruction == "Be concise and accurate."

    def test_fields_accept_none(self):
        """Each field may be explicitly set to None."""
        dto = PromptDTO(introduction=None, target=None, instruction=None)
        assert dto.introduction is None
        assert dto.target is None
        assert dto.instruction is None

    def test_empty_construction_is_valid(self):
        """A PromptDTO can be built without any argument."""
        assert isinstance(PromptDTO(), PromptDTO)

    def test_extra_fields_are_ignored(self):
        """Unknown keyword arguments do not raise an error."""
        dto = PromptDTO(extra_field="ignored")
        assert dto.model_dump() == {
            "introduction": "",
            "target": "",
            "instruction": "",
        }

    def test_model_dump_round_trip(self, prompt_dto):
        """model_dump returns a plain dict reconstructing an equal model."""
        data = prompt_dto.model_dump()
        assert data["target"] == "Answer user questions."
        assert PromptDTO(**data) == prompt_dto
