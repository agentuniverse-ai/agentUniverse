# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 17:00
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: run_command_tool.py

import os
import json
import time
import threading
import subprocess
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class CommandStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class CommandResult:
    thread_id: int
    stdout: str
    stderr: str
    start_time: float
    status: CommandStatus
    exit_code: Optional[int] = None
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    @property
    def message(self) -> str:
        # Truncate stdout and stderr if they are too long
        max_output_length = 2000
        truncated_stdout = self._truncate_output(
            self.stdout, max_output_length)
        truncated_stderr = self._truncate_output(
            self.stderr, max_output_length)

        result_dict = {
            'thread_id': self.thread_id,
            'status': self.status.value,
            'stdout': truncated_stdout,
            'stderr': truncated_stderr,
            'exit_code': self.exit_code,
            'duration': self.duration
        }
        return json.dumps(result_dict)

    def _truncate_output(self, output: str, max_length: int) -> str:
        """Truncate output to keep beginning and end, removing middle when too long"""
        if not output or len(output) <= max_length:
            return output
        half_length = max_length // 2
        return output[:half_length] + "\n... [truncated output] ...\n" + output[-half_length:]


_command_results: Dict[int, CommandResult] = {}


class RunCommandTool(Tool):
    """
    Tool for executing shell commands either synchronously or asynchronously.
    """

    def execute(self, command: str, cwd: str, blocking: bool = True) -> str:
        return self._run_command(command, cwd, blocking)

    def _run_command(self, command: str, cwd: str, blocking: bool = True) -> str:
        result = CommandResult(
            thread_id=threading.get_ident(),
            status=CommandStatus.RUNNING,
            stdout="",
            stderr="",
            start_time=time.time(),
        )

        def __run() -> None:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )

                stdout, stderr = process.communicate()
                exit_code = process.returncode

                result.stdout = stdout
                result.stderr = stderr
                result.exit_code = exit_code
                result.end_time = time.time()
                result.status = CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.ERROR

            except Exception as e:
                result.stderr = str(e)
                result.end_time = time.time()
                result.status = CommandStatus.ERROR

            _command_results[result.thread_id] = result

        if blocking:
            __run()
        else:
            thread = threading.Thread(target=__run)
            thread.start()
            result.thread_id = thread.ident
            _command_results[result.thread_id] = result

        return result.message


def get_command_result(thread_id: int) -> Optional[CommandResult]:
    return _command_results.get(thread_id)
