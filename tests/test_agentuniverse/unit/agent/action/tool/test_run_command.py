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
import sys
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
        # Opt in explicitly: RunCommandTool is disabled by default because it
        # runs arbitrary shell commands (see allow_command_execution).
        """Opt in explicitly since RunCommandTool is disabled by default, then build the tool."""
        self.tool = RunCommandTool(allow_command_execution=True)

    def test_disabled_by_default_refuses(self) -> None:
        """A default RunCommandTool must refuse to execute anything."""
        tool = RunCommandTool()
        result = json.loads(tool.execute(ToolInput({
            'command': 'echo should_not_run', 'blocking': True})))
        self.assertEqual(result['status'], CommandStatus.ERROR.value)
        self.assertNotIn('should_not_run', result.get('stdout', ''))
        self.assertIn('allow_command_execution', result['stderr'])

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
            'command': f'"{sys.executable}" -c "import time; time.sleep(1); print(\'Async Test\')"',
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

    def test_string_false_blocking_value_runs_nonblocking(self) -> None:
        """Verify the string 'false' blocking value is treated as non-blocking execution."""
        tool_input = ToolInput({
            'command': f'"{sys.executable}" -c "import time; time.sleep(0.5); print(\'String False\')"',
            'cwd': os.getcwd(),
            'blocking': 'false'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], CommandStatus.RUNNING.value)
        cmd_result = get_command_result(result['thread_id'])
        self.assertIsNotNone(cmd_result)
        self.assertEqual(cmd_result.status, CommandStatus.RUNNING)

    def test_typo_blocking_value_returns_input_error(self) -> None:
        """Verify a misspelled blocking value returns an input error."""
        tool_input = ToolInput({
            'command': 'echo "should not run"',
            'cwd': os.getcwd(),
            'blocking': 'flase'
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], CommandStatus.ERROR.value)
        self.assertIn('blocking must be a boolean value', result['error'])

    def test_non_binary_numeric_blocking_value_returns_input_error(self) -> None:
        """Verify a numeric blocking value other than 0 or 1 returns an input error."""
        tool_input = ToolInput({
            'command': 'echo "should not run"',
            'cwd': os.getcwd(),
            'blocking': 2
        })

        result_json = self.tool.execute(tool_input)
        result = json.loads(result_json)

        self.assertEqual(result['status'], CommandStatus.ERROR.value)
        self.assertIn('blocking numeric value must be 0 or 1', result['error'])

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
            'command': f'"{sys.executable}" -c "import sys; sys.stdout.write(\'Line 1\\\\nLine 2\\\\tTabbed\\\\r\\\\nWindows\' + chr(34) + \'Quote\' + chr(34))"',
            'cwd': os.getcwd(),
            'blocking': True
        })
        result_json = self.tool.execute(tool_input)

        result = json.loads(result_json)
        self.assertIn('thread_id', result)
        self.assertIn('Line 1', result['stdout'])
        self.assertIn('Line 2', result['stdout'])
        self.assertIn('Quote', result['stdout'])

    def test_nonblocking_popen_exception(self) -> None:
        """Popen exception in non-blocking mode returns the error directly,
        never a 'started=running' acknowledgement."""
        import subprocess as _real_subprocess
        original_popen = _real_subprocess.Popen

        def _failing_popen(*args, **kwargs):
            raise OSError("fake_device_busy: resource temporarily unavailable")

        # Patch Popen at the module level so RunCommandTool.__run sees it.
        import agentuniverse.agent.action.tool.common_tool.run_command_tool as rct
        rct.subprocess.Popen = _failing_popen
        try:
            result_json = self.tool.execute(ToolInput({
                'command': 'echo should_not_run',
                'cwd': os.getcwd(),
                'blocking': False
            }))
        finally:
            rct.subprocess.Popen = original_popen

        result = json.loads(result_json)
        self.assertEqual(result['status'], CommandStatus.ERROR.value,
                         "Popen failure must surface as ERROR, not RUNNING")
        self.assertIn('fake_device_busy', result.get('stderr', ''),
                      "The OSError message must be propagated in stderr")
        self.assertNotIn('started', result,
                         "No 'started' key should appear on a Popen failure")
        self.assertNotIn('thread_id', result,
                         "No 'thread_id' key should appear on a Popen failure")

    def test_nonblocking_successful_acknowledgement(self) -> None:
        """Successful non-blocking start returns a proper acknowledgement:
        status=running with thread_id."""
        result_json = self.tool.execute(ToolInput({
            'command': f'"{sys.executable}" -c "import time; time.sleep(0.3); print(\'done\')"',
            'cwd': os.getcwd(),
            'blocking': False
        }))
        result = json.loads(result_json)

        self.assertEqual(result['status'], CommandStatus.RUNNING.value)
        self.assertTrue(result.get('started'))
        self.assertIn('thread_id', result)
        self.assertIsInstance(result['thread_id'], int)

        # The command should eventually complete
        thread_id = result['thread_id']
        for _ in range(5):
            cmd_result = get_command_result(thread_id)
            if cmd_result and cmd_result.status != CommandStatus.RUNNING:
                break
            time.sleep(0.5)

        cmd_result = get_command_result(thread_id)
        self.assertIsNotNone(cmd_result)
        self.assertEqual(cmd_result.status, CommandStatus.COMPLETED)
        self.assertIn('done', cmd_result.stdout)


if __name__ == '__main__':
    unittest.main()
