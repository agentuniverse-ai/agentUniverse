# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_message_do.py

"""Unit tests for the MessageDO."""

import datetime

import pytest

from agentuniverse_product.dal.model.message_do import MessageDO


class TestMessageDO:
    """Test MessageDO model defaults and construction."""

    def test_construction_and_defaults(self):
        do = MessageDO(session_id="s1")
        assert do.id is None
        assert do.session_id == "s1"
        assert do.content == ""
        assert do.ext_info == {}
        assert isinstance(do.gmt_created, datetime.datetime)

    def test_required_session_id(self):
        with pytest.raises(Exception):
            MessageDO()

    def test_explicit_content_and_ext_info(self):
        do = MessageDO(session_id="s1", content="hello",
                       ext_info={"role": "user"})
        assert do.content == "hello"
        assert do.ext_info == {"role": "user"}

    def test_equality_ignoring_timestamps(self):
        fields = {"session_id", "content", "ext_info"}
        first = MessageDO(session_id="s1")
        second = MessageDO(session_id="s1")
        assert {k: getattr(first, k) for k in fields} == \
            {k: getattr(second, k) for k in fields}
        assert MessageDO(session_id="s1").session_id != \
            MessageDO(session_id="s2").session_id
