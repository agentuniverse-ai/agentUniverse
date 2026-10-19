# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_command_status_tool.py
"""Unit tests for CommandStatusTool."""

import json

import pytest

from agentuniverse.agent.action.tool.common_tool.command_status_tool import CommandStatusTool
from agentuniverse.agent.action.tool.common_tool.run_command_tool import RunCommandTool
from agentuniverse.agent.action.tool.tool import ToolInput


class TestCommandStatusTool:
    def test_normalize_thread_id(self):
        assert CommandStatusTool._normalize_thread_id(3) == 3
        assert CommandStatusTool._normalize_thread_id('42') == 42

    def test_normalize_thread_id_rejects_invalid(self):
        with pytest.raises(ValueError):
            CommandStatusTool._normalize_thread_id('abc')
        with pytest.raises(ValueError):
            CommandStatusTool._normalize_thread_id(True)

    def test_execute_missing_thread(self):
        result = json.loads(CommandStatusTool().execute(999999999))
        assert result['status'] == 'not_found'

    def test_execute_invalid_id(self):
        result = json.loads(CommandStatusTool().execute('abc'))
        assert result['status'] == 'error'

    def test_execute_tool_input_style(self):
        result = json.loads(CommandStatusTool().execute(ToolInput({'thread_id': '999999998'})))
        assert result['status'] == 'not_found'

    def test_execute_registered_thread(self):
        run_result = json.loads(RunCommandTool(allow_command_execution=True).execute(
            ToolInput({'command': 'echo status-0184', 'blocking': True})))
        thread_id = run_result['thread_id']
        result = json.loads(CommandStatusTool().execute(thread_id))
        assert 'status-0184' in result['stdout']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
