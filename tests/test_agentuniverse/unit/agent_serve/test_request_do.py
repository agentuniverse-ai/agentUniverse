# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/6/21
# @FileName: test_request_do.py

import pytest

from agentuniverse.agent_serve.web.dal.entity.request_do import RequestDO


def _make_request_do(query) -> RequestDO:
    """Helper to build a RequestDO with only the required fields."""
    return RequestDO(
        request_id="test-request-id",
        session_id="test-session-id",
        query=query,
        state="init",
        result=dict(),
        steps=[],
        additional_args=dict(),
    )


def test_request_do_accepts_string_query():
    request_do = _make_request_do("what is the weather today?")
    assert request_do.query == "what is the weather today?"


def test_request_do_accepts_list_query():
    query = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    request_do = _make_request_do(query)
    assert request_do.query == query


def test_request_do_accepts_dict_query():
    query = {"input": "hello", "context": {"lang": "zh"}}
    request_do = _make_request_do(query)
    assert request_do.query == query


def test_request_do_model_dump_preserves_non_string_query():
    query = {"input": "hello"}
    request_do = _make_request_do(query)
    dumped = request_do.model_dump()
    assert dumped["query"] == query


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
