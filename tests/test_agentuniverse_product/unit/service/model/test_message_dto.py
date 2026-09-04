# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08
# @Author  : Yue Wang
# @FileName: test_message_dto.py
"""Unit tests for the MessageDTO pydantic model."""

import pytest
from pydantic import ValidationError

from agentuniverse_product.service.model.message_dto import MessageDTO


class TestMessageDTO:
    """Test MessageDTO field defaults, validation and serialization."""

    @pytest.fixture
    def message_dto(self) -> MessageDTO:
        """Return a fully populated MessageDTO instance."""
        return MessageDTO(
            id=1,
            session_id="session-1",
            content="hello",
            gmt_created="2024-01-01 10:00:00",
            gmt_modified="2024-01-01 10:05:00",
        )

    def test_content_default_is_empty_string(self):
        """content falls back to an empty string when not provided."""
        dto = MessageDTO(id=1, session_id="s1",
                         gmt_created="2024-01-01", gmt_modified="2024-01-01")
        assert dto.content == ""
        assert dto.gmt_created == "2024-01-01"
        assert dto.gmt_modified == "2024-01-01"

    def test_explicit_values_stored(self, message_dto):
        """Explicitly provided constructor values are preserved."""
        assert message_dto.id == 1
        assert message_dto.session_id == "session-1"
        assert message_dto.content == "hello"
        assert message_dto.gmt_modified == "2024-01-01 10:05:00"

    def test_session_id_is_required(self):
        """Creating a MessageDTO without a session_id raises a validation error."""
        with pytest.raises(ValidationError):
            MessageDTO(id=1, gmt_created="2024-01-01", gmt_modified="2024-01-01")

    def test_id_must_be_integer(self):
        """A non-integer id is rejected."""
        with pytest.raises(ValidationError):
            MessageDTO(id="not-an-int", session_id="s1",
                       gmt_created="2024-01-01", gmt_modified="2024-01-01")

    def test_gmt_fields_are_required(self):
        """Omitting the gmt_created and gmt_modified fields raises a validation error."""
        with pytest.raises(ValidationError):
            MessageDTO(id=1, session_id="s1")

    def test_content_accepts_none(self):
        """content may be explicitly set to None."""
        dto = MessageDTO(id=2, session_id="s1", content=None,
                         gmt_created="2024-01-01", gmt_modified="2024-01-01")
        assert dto.content is None

    def test_model_dump_round_trip(self, message_dto):
        """model_dump returns a plain dict reconstructing an equal model."""
        data = message_dto.model_dump()
        assert data["id"] == 1
        assert data["content"] == "hello"
        assert MessageDTO(**data) == message_dto
