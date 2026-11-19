# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_post_fork_queue.py

"""Unit tests for the post-fork callback queue."""

import pytest

from agentuniverse.agent_serve.web.post_fork_queue import (
    POST_FORK_QUEUE,
    add_post_fork,
)


@pytest.fixture(autouse=True)
def clean_queue():
    """Remove entries appended during the test."""
    baseline = len(POST_FORK_QUEUE)
    yield
    del POST_FORK_QUEUE[baseline:]


class TestPostForkQueue:
    """Test add_post_fork queueing semantics."""

    def test_plain_callable_is_queued(self):
        def handler():
            return 1

        add_post_fork(handler)
        assert len(POST_FORK_QUEUE) == 1
        func, args, kwargs = POST_FORK_QUEUE[-1]
        assert func is handler
        assert args == ()
        assert kwargs == {}

    def test_args_and_kwargs_are_kept(self):
        def handler(a, b, c=None):
            return a

        add_post_fork(handler, 1, 2, c=3)
        func, args, kwargs = POST_FORK_QUEUE[-1]
        assert func is handler
        assert args == (1, 2)
        assert kwargs == {"c": 3}

    def test_multiple_callbacks_preserve_order(self):
        calls = []

        def first():
            calls.append("first")

        def second():
            calls.append("second")

        add_post_fork(first)
        add_post_fork(second)
        assert [cb for cb, _, _ in POST_FORK_QUEUE[-2:]] == [first, second]
