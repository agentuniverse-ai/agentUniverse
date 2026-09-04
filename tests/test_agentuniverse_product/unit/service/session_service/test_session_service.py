# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/01 10:00
# @Author  : Yue Wang
# @FileName: test_session_service.py
"""Unit tests for the session_service module."""

from datetime import datetime

import pytest

from agentuniverse_product.dal.model.message_do import MessageDO
from agentuniverse_product.dal.model.session_do import SessionDO
from agentuniverse_product.service.session_service.session_service import SessionService


def make_session(session_id: str, agent_id: str = "agent_1") -> SessionDO:
    """Build a SessionDO with fixed timestamps."""
    return SessionDO(session_id=session_id, agent_id=agent_id, gmt_created=datetime(2024, 1, 1, 10, 0, 0), gmt_modified=datetime(2024, 1, 2, 11, 30, 0))


def make_message(message_id: int, session_id: str, content: str) -> MessageDO:
    """Build a MessageDO with fixed timestamps."""
    return MessageDO(id=message_id, session_id=session_id, content=content, gmt_created=datetime(2024, 1, 1, 10, 0, 1), gmt_modified=datetime(2024, 1, 1, 10, 0, 2))


class TestConvertToSessionDto:
    """Tests for the pure convert_to_session_dto conversion."""

    def test_empty_session_list_returns_empty(self):
        """An empty session list converts to an empty dto list."""
        assert SessionService().convert_to_session_dto([], {}) == []

    def test_session_without_messages(self):
        """A session without messages keeps an empty message list."""
        session_do = make_session("s1")
        dtos = SessionService().convert_to_session_dto([session_do], {"s1": []})

        assert len(dtos) == 1
        assert dtos[0].id == "s1"
        assert dtos[0].agent_id == "agent_1"
        assert dtos[0].gmt_created == "2024-01-01 10:00:00"
        assert dtos[0].gmt_modified == "2024-01-02 11:30:00"
        assert dtos[0].messages == []

    def test_session_with_messages(self):
        """Messages are converted with id, session id, content and times."""
        session_do = make_session("s2")
        message_do = make_message(7, "s2", "hello")
        dtos = SessionService().convert_to_session_dto([session_do], {"s2": [message_do]})

        message_dto = dtos[0].messages[0]
        assert message_dto.id == 7
        assert message_dto.session_id == "s2"
        assert message_dto.content == "hello"
        assert message_dto.gmt_created == "2024-01-01 10:00:01"

    def test_multiple_sessions_preserve_order(self):
        """Session dto order follows the input session do order."""
        first = make_session("a")
        second = make_session("b", agent_id="agent_2")
        dtos = SessionService().convert_to_session_dto([first, second], {"a": [], "b": []})

        assert [dto.id for dto in dtos] == ["a", "b"]
        assert dtos[1].agent_id == "agent_2"


class TestSessionServiceValidation:
    """Tests for parameter validation of the service methods."""

    def test_create_session_requires_agent_id(self):
        """create_session raises when agent_id is None."""
        with pytest.raises(ValueError, match="agent_id is required parameter."):
            SessionService.create_session(None)

    def test_delete_session_requires_session_id(self):
        """delete_session raises when session_id is None."""
        with pytest.raises(ValueError, match="session_id is required parameter."):
            SessionService.delete_session(None)

    def test_get_session_list_requires_agent_id(self):
        """get_session_list raises when agent_id is None."""
        with pytest.raises(ValueError, match="agent_id is required parameter."):
            SessionService.get_session_list(None)

    def test_get_session_detail_requires_id(self):
        """get_session_detail raises when id is None."""
        with pytest.raises(ValueError, match="Session id is required parameter."):
            SessionService.get_session_detail(None)
