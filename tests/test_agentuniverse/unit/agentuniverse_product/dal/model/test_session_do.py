# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_session_do.py

"""Unit tests for the SessionDO."""

import datetime

import pytest

from agentuniverse_product.dal.model.session_do import SessionDO


class TestSessionDO:
    """Test SessionDO model defaults and construction."""

    def test_construction_and_defaults(self):
        do = SessionDO(session_id="s1", agent_id="a1")
        assert do.id is None
        assert do.session_id == "s1"
        assert do.agent_id == "a1"
        assert do.ext_info == {}
        assert isinstance(do.gmt_created, datetime.datetime)

    def test_required_fields(self):
        with pytest.raises(Exception):
            SessionDO(session_id="s1")
        with pytest.raises(Exception):
            SessionDO(agent_id="a1")

    def test_explicit_times_and_ext_info(self):
        when = datetime.datetime(2024, 1, 1, 12, 0, 0)
        do = SessionDO(session_id="s1", agent_id="a1",
                       ext_info={"k": "v"}, gmt_created=when,
                       gmt_modified=when)
        assert do.ext_info == {"k": "v"}
        assert do.gmt_created == when

    def test_equality_ignoring_timestamps(self):
        fields = {"session_id", "agent_id", "id", "ext_info"}
        first = SessionDO(session_id="s1", agent_id="a1")
        second = SessionDO(session_id="s1", agent_id="a1")
        assert {k: getattr(first, k) for k in fields} == \
            {k: getattr(second, k) for k in fields}
        assert SessionDO(session_id="s1", agent_id="a1").session_id != \
            SessionDO(session_id="s2", agent_id="a1").session_id
