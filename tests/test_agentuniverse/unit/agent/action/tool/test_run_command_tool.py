# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_run_command_tool.py
"""Unit tests for RunCommandTool."""

import json
import time

import pytest

from agentuniverse.agent.action.tool.common_tool.run_command_tool import (
    CommandStatus,
    RunCommandTool,
    get_command_result,
)
from agentuniverse.agent.action.tool.tool import ToolInput


class TestRunCommandTool:
    @pytest.fixture
    def tool(self):
        return RunCommandTool(allow_command_execution=True)

    def test_disabled_by_default_refuses(self):
        tool = RunCommandTool()
        result = json.loads(tool.execute(ToolInput({'command': 'echo nope', 'blocking': True})))
        assert result['status'] == CommandStatus.ERROR.value
        assert 'allow_command_execution' in result['stderr']

    def test_blocking_echo(self, tool):
        result = json.loads(tool.execute(ToolInput({'command': 'echo hello-au-0181', 'blocking': True})))
        assert result['status'] == CommandStatus.COMPLETED.value
        assert 'hello-au-0181' in result['stdout']
        assert result['exit_code'] == 0

    def test_blocking_result_registered(self, tool):
        result = json.loads(tool.execute(ToolInput({'command': 'echo registered-run', 'blocking': True})))
        thread_id = result['thread_id']
        command_result = get_command_result(thread_id)
        assert command_result is not None
        assert 'registered-run' in command_result.stdout

    def test_nonblocking_becomes_completed(self, tool):
        result = json.loads(tool.execute(ToolInput({
            'command': 'echo async-run-0181; sleep 0.2', 'blocking': False})))
        assert result['status'] == CommandStatus.RUNNING.value
        thread_id = result['thread_id']
        final = None
        for _ in range(20):
            current = get_command_result(thread_id)
            if current and current.status != CommandStatus.RUNNING:
                final = current
                break
            time.sleep(0.1)
        assert final is not None
        assert final.status == CommandStatus.COMPLETED
        assert 'async-run-0181' in final.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
