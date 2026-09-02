# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:30
# @Author  : yuewang
# @FileName: test_post_fork_queue.py
"""Unit tests for the post-fork queue helpers."""

import pytest

from agentuniverse.agent_serve.web.post_fork_queue import (
    POST_FORK_QUEUE,
    add_post_fork,
)


@pytest.fixture(autouse=True)
def clean_queue():
    """Ensure the module-level queue starts and ends empty."""
    saved = list(POST_FORK_QUEUE)
    POST_FORK_QUEUE.clear()
    yield
    POST_FORK_QUEUE.clear()
    POST_FORK_QUEUE.extend(saved)


def test_queue_starts_empty(clean_queue):
    assert POST_FORK_QUEUE == []


def test_add_post_fork_appends_entry():
    def target():
        return 'ok'

    add_post_fork(target)
    assert len(POST_FORK_QUEUE) == 1
    func, args, kwargs = POST_FORK_QUEUE[0]
    assert func is target
    assert args == ()
    assert kwargs == {}


def test_add_post_fork_keeps_args_and_order():
    add_post_fork(lambda a, b: a + b, 1, 2)
    add_post_fork(lambda: 'second')
    assert len(POST_FORK_QUEUE) == 2
    first_func, first_args, _ = POST_FORK_QUEUE[0]
    assert first_func(1, 2) == 3
    second_func, second_args, _ = POST_FORK_QUEUE[1]
    assert second_func() == 'second'


def test_add_post_fork_kwargs():
    add_post_fork(lambda: None, key='value')
    _, _, kwargs = POST_FORK_QUEUE[0]
    assert kwargs == {'key': 'value'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
