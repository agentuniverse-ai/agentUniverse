# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/22 18:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: test_run_command.py

import unittest
import time
import json
import os
from agentuniverse.agent.action.tool.common_tool.run_command_tool import (
    RunCommandTool,
    CommandStatus,
    get_command_result
)
from agentuniverse.agent.action.tool.tool import ToolInput


class RunCommandToolTest(unittest.TestCase):
    """
    Test cases for RunCommandTool class
    """

    def setUp(self) -> None:
        self.tool = RunCommandTool()

    def test_blocking_command_execution(self) -> None:
        """Test synchronous command execution"""
        tool_input = ToolInput({
            'command': 'echo "Hello World"',
            'cwd': os.getcwd(),
            'blocking': True
        })
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertIn('thread_id', result)
        self.assertEqual(result['status'], CommandStatus.COMPLETED.value)
        self.assertIn('Hello World', result['stdout'])
        self.assertEqual(result['stderr'], '')
        self.assertEqual(result['exit_code'], 0)

        cmd_result = get_command_result(result['thread_id'])
        self.assertIsNotNone(cmd_result)
        self.assertEqual(cmd_result.status, CommandStatus.COMPLETED)
        self.assertIn('Hello World', cmd_result.stdout)

    def test_nonblocking_command_execution(self) -> None:
        """Test asynchronous command execution"""
        tool_input = ToolInput({
            'command': 'sleep 1 && echo "Async Test"',
            'cwd': os.getcwd(),
            'blocking': False
        })
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertIn('thread_id', result)
        self.assertEqual(result['status'], CommandStatus.RUNNING.value)

        thread_id = result['thread_id']
        for _ in range(3):
            cmd_result = get_command_result(thread_id)
            if cmd_result and cmd_result.status != CommandStatus.RUNNING:
                break
            time.sleep(0.5)

        cmd_result = get_command_result(thread_id)
        self.assertIsNotNone(cmd_result)
        self.assertEqual(cmd_result.status, CommandStatus.COMPLETED)
        self.assertIn('Async Test', cmd_result.stdout)
        self.assertEqual(cmd_result.exit_code, 0)

    def test_command_error(self) -> None:
        """Test handling of commands that result in errors"""
        tool_input = ToolInput({
            'command': 'command_that_does_not_exist',
            'cwd': os.getcwd(),
            'blocking': True
        })
        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertIn('thread_id', result)
        self.assertEqual(result['status'], CommandStatus.ERROR.value)
        self.assertNotEqual(result['stderr'], '')
        self.assertNotEqual(result['exit_code'], 0)

    def test_command_output_escaping(self) -> None:
        """Test that special characters in command output are properly escaped"""
        tool_input = ToolInput({
            'command': 'echo "Line 1\nLine 2\tTabbed\r\nWindows\\"Quote\\""',
            'cwd': os.getcwd(),
            'blocking': True
        })
        result_json = self.tool.execute(tool_input)

        result = json.loads(result_json)
        self.assertIn('thread_id', result)
        self.assertIn('Line 1', result['stdout'])
        self.assertIn('Line 2', result['stdout'])
        self.assertIn('Quote', result['stdout'])


if __name__ == '__main__':
    unittest.main()
