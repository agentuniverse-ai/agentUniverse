# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08
# @Author  : Yue Wang
# @FileName: test_session_dto.py
"""Unit tests for the SessionDTO pydantic model."""

import pytest
from pydantic import ValidationError

from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO


class TestSessionDTO:
    """Test SessionDTO field defaults, validation and serialization."""

    @pytest.fixture
    def session_dto(self) -> SessionDTO:
        """Return a fully populated SessionDTO instance."""
        return SessionDTO(
            id="session-1",
            agent_id="agent-1",
            messages=[
                {"id": 1, "session_id": "session-1", "content": "hi",
                 "gmt_created": "2024-01-01", "gmt_modified": "2024-01-01"}
            ],
            gmt_created="2024-01-01",
            gmt_modified="2024-01-02",
        )

    def test_default_messages_is_empty_list(self):
        """messages defaults to an empty list when not provided."""
        dto = SessionDTO(id="s1", agent_id="a1",
                         gmt_created="2024-01-01", gmt_modified="2024-01-01")
        assert dto.messages == []
        assert dto.gmt_created == "2024-01-01"
        assert dto.gmt_modified == "2024-01-01"

    def test_explicit_values_stored(self, session_dto):
        """Explicitly provided constructor values are preserved."""
        assert session_dto.id == "session-1"
        assert session_dto.agent_id == "agent-1"
        assert session_dto.gmt_modified == "2024-01-02"

    def test_agent_id_is_required(self):
        """Creating a SessionDTO without an agent_id raises a validation error."""
        with pytest.raises(ValidationError):
            SessionDTO(id="s1", gmt_created="2024-01-01", gmt_modified="2024-01-01")

    def test_message_dicts_coerced_to_message_dto(self, session_dto):
        """Nested message dicts are coerced into MessageDTO instances."""
        assert isinstance(session_dto.messages[0], MessageDTO)
        assert session_dto.messages[0].content == "hi"

    def test_model_dump_round_trip(self, session_dto):
        """model_dump returns a plain dict reconstructing an equal model."""
        data = session_dto.model_dump()
        assert data["id"] == "session-1"
        assert data["messages"][0]["content"] == "hi"
        assert SessionDTO(**data) == session_dto

    def test_messages_accept_message_dto_instances(self):
        """messages also accepts already-built MessageDTO instances."""
        message = MessageDTO(id=2, session_id="s1", content="yo",
                             gmt_created="2024-01-01", gmt_modified="2024-01-01")
        dto = SessionDTO(id="s2", agent_id="a2", messages=[message],
                         gmt_created="2024-01-01", gmt_modified="2024-01-01")
        assert dto.messages == [message]
