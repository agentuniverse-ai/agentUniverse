# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 18:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_command_status.py

import os
import json
import sys
import time
import unittest

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.run_command_tool import (
    RunCommandTool,
    CommandStatus,
)
from agentuniverse.agent.action.tool.common_tool.command_status_tool import CommandStatusTool


class CommandStatusToolTest(unittest.TestCase):
    """Unit tests for the CommandStatusTool thread-status lookup."""
    def setUp(self):
        """Create a RunCommandTool and a CommandStatusTool for the tests."""
        self.run_tool = RunCommandTool(allow_command_execution=True)
        self.status_tool = CommandStatusTool()

    def test_command_status_check(self):
        """Verify querying a completed command's thread id returns its status and stdout."""
        tool_input = ToolInput({
            'command': 'echo "Hello World"',
            'cwd': os.getcwd(),
            'blocking': True
        })
        result_json = self.run_tool.execute(tool_input)
        result = json.loads(result_json)
        thread_id = result['thread_id']
        
        status_input = ToolInput({
            'thread_id': thread_id
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)
        
        self.assertEqual(status_result['thread_id'], thread_id)
        self.assertEqual(status_result['status'], CommandStatus.COMPLETED.value)
        self.assertIn('Hello World', status_result['stdout'])
        self.assertEqual(status_result['exit_code'], 0)

    def test_running_command_status(self):
        """Verify a non-blocking command is reported running and completes with output later."""
        tool_input = ToolInput({
            'command': f'"{sys.executable}" -c "import time; time.sleep(2); print(\'Long running command finished\')"',
            'cwd': os.getcwd(),
            'blocking': False
        })
        result_json = self.run_tool.execute(tool_input)
        result = json.loads(result_json)
        thread_id = result['thread_id']
        
        status_input = ToolInput({
            'thread_id': thread_id
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)        
        
        time.sleep(3)
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)
        
        self.assertEqual(status_result['status'], CommandStatus.COMPLETED.value)
        self.assertIn('Long running command finished', status_result['stdout'])
        self.assertEqual(status_result['exit_code'], 0)

    def test_invalid_thread_id(self):
        """Verify querying a nonexistent numeric thread id returns a not_found error."""
        status_input = ToolInput({
            'thread_id': 12345678  # A thread ID that shouldn't exist
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)
        
        self.assertIn('error', status_result)
        self.assertEqual(status_result['status'], 'not_found')

    def test_string_thread_id_is_parsed(self):
        """Verify a numeric string thread id is parsed and yields a not_found error for an unknown id."""
        status_input = ToolInput({
            'thread_id': '12345678'
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)

        self.assertIn('error', status_result)
        self.assertEqual(status_result['status'], 'not_found')

    def test_malformed_thread_id_returns_input_error(self):
        """Verify a non-numeric thread id returns an input error."""
        status_input = ToolInput({
            'thread_id': 'abc'
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)

        self.assertEqual(status_result['status'], 'error')
        self.assertIn('thread_id must be an integer', status_result['error'])

    def test_boolean_thread_id_returns_input_error(self):
        """Verify a boolean thread id returns an input error."""
        status_input = ToolInput({
            'thread_id': True
        })
        status_json = self.status_tool.execute(status_input)
        status_result = json.loads(status_json)

        self.assertEqual(status_result['status'], 'error')
        self.assertIn('thread_id must be an integer', status_result['error'])


if __name__ == '__main__':
    unittest.main()
