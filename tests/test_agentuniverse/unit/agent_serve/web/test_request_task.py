# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_request_task.py

"""Unit tests for RequestTask state handling (no database persistence)."""

import pytest

from agentuniverse.agent_serve.web.request_task import (
    EOF_SIGNAL,
    RequestTask,
    TaskStateEnum,
    VALID_TRANSITIONS,
)


def ok_func():
    return "done"


def fail_func():
    raise RuntimeError("boom")


@pytest.fixture
def task():
    return RequestTask(func=ok_func, saved=False)


class TestRequestTaskStates:
    """Test RequestTask initialization and state transitions."""

    def test_initial_state_and_request_id(self, task):
        assert task.request_state() == TaskStateEnum.INIT.value
        assert task.request_id

    def test_run_success(self, task):
        assert task.run() == "done"
        assert task.request_state() == TaskStateEnum.FINISHED.value

    def test_run_failure_raises_and_marks_fail(self):
        task = RequestTask(func=fail_func, saved=False)
        with pytest.raises(RuntimeError, match="boom"):
            task.run()
        assert task.request_state() == TaskStateEnum.FAIL.value

    def test_next_state_valid_transition(self, task):
        task.next_state(TaskStateEnum.RUNNING)
        assert task.request_state() == TaskStateEnum.RUNNING.value

    def test_next_state_invalid_transition_raises(self, task):
        with pytest.raises(Exception, match="Invalid state transition"):
            task.next_state(TaskStateEnum.FINISHED)

    def test_cancel_puts_eof_and_marks_canceled(self, task):
        task.cancel()
        assert task.canceled() is True
        assert task.request_state() == TaskStateEnum.CANCELED.value
        assert task.queue.get_nowait() == EOF_SIGNAL

    def test_finished_flag(self, task):
        task.finished()
        assert task.request_state() == TaskStateEnum.FINISHED.value

    def test_task_state_enum_values(self):
        assert TaskStateEnum.INIT.value == "init"
        assert TaskStateEnum.RUNNING.value == "running"
        assert TaskStateEnum.FINISHED.value == "finished"
        assert TaskStateEnum.FAIL.value == "fail"
        assert TaskStateEnum.CANCELED.value == "canceled"

    def test_valid_transitions_contained(self):
        assert (TaskStateEnum.INIT, TaskStateEnum.RUNNING) in VALID_TRANSITIONS
        assert (TaskStateEnum.RUNNING, TaskStateEnum.FINISHED) in \
            VALID_TRANSITIONS
        assert (TaskStateEnum.INIT, TaskStateEnum.FINISHED) not in \
            VALID_TRANSITIONS
