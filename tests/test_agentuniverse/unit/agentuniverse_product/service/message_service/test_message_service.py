# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_message_service.py

"""Unit tests for the MessageService."""

from datetime import datetime
from unittest.mock import patch

import pytest

import agentuniverse_product.service.message_service.message_service as ms
from agentuniverse_product.dal.model.message_do import MessageDO
from agentuniverse_product.service.message_service.message_service import \
    MessageService


class FakeMessageLibrary:
    def __init__(self):
        self.added = []

    def add_message(self, message_do):
        self.added.append(message_do)
        return 42


class TestMessageService:
    """Test add_message parameter handling and delegation."""

    def test_none_content_raises(self):
        with pytest.raises(ValueError, match="message content is required"):
            MessageService.add_message("s1", None, datetime.now())

    def test_add_message_builds_message_do(self):
        fake = FakeMessageLibrary()
        when = datetime(2024, 1, 1, 12, 0, 0)
        with patch.object(ms, "MessageLibrary", return_value=fake):
            result = MessageService.add_message("s1", "hello", when)
        assert result == 42
        assert len(fake.added) == 1
        message_do = fake.added[0]
        assert isinstance(message_do, MessageDO)
        assert message_do.session_id == "s1"
        assert message_do.content == "hello"
        assert message_do.gmt_created == when
        assert message_do.gmt_modified == when

    def test_empty_content_is_allowed(self):
        fake = FakeMessageLibrary()
        with patch.object(ms, "MessageLibrary", return_value=fake):
            MessageService.add_message("s1", "", datetime.now())
        assert len(fake.added) == 1
