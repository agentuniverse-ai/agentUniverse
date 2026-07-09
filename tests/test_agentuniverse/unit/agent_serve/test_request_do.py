# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/06
# @FileName: test_request_do.py

import pytest

from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO


def test_request_do_with_string_query():
    """RequestDO should accept a string query."""
    do = RequestDO(
        request_id="req-1",
        session_id="sess-1",
        query="hello world",
        state="init",
        result=dict(),
        steps=[],
        additional_args=dict(),
    )
    assert do.query == "hello world"


def test_request_do_with_list_query():
    """RequestDO should accept a list query (issue #583)."""
    query_list = ["item1", "item2"]
    do = RequestDO(
        request_id="req-2",
        session_id="sess-2",
        query=query_list,
        state="init",
        result=dict(),
        steps=[],
        additional_args=dict(),
    )
    assert do.query == query_list


def test_request_do_with_dict_query():
    """RequestDO should accept a dict query (issue #583)."""
    query_dict = {"key": "value"}
    do = RequestDO(
        request_id="req-3",
        session_id="sess-3",
        query=query_dict,
        state="init",
        result=dict(),
        steps=[],
        additional_args=dict(),
    )
    assert do.query == query_dict


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
