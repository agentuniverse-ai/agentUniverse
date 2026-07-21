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
from agentuniverse.agent.action.tool.common_tool.tool_input_utils import parse_strict_bool
from loguru import logger


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
    """Tool for executing shell commands either synchronously or asynchronously.

    .. warning::
        **Security:** this tool runs **arbitrary shell commands on the host**
        via ``subprocess`` with ``shell=True``. There is no sandboxing, command
        allow-list, or resource limiting. A prompt injection that reaches this
        tool escalates directly to arbitrary command execution and full host
        compromise.

        Because of that, the tool is **disabled by default**, mirroring
        :class:`PythonREPLTool`. Set ``allow_command_execution: True`` to opt
        in, and only do so in a fully trusted, isolated environment. Do not
        equip an agent that processes untrusted input (documents, web pages,
        chat messages) with this tool.

    Attributes:
        allow_command_execution (bool): Explicit opt-in flag. Defaults to
            ``False`` so the tool refuses to execute commands until an
            integrator acknowledges the risk above.
    """

    allow_command_execution: bool = False

    def execute(self, command: str | ToolInput, cwd: str = None, blocking: bool = True) -> str:
        if isinstance(command, ToolInput):
            params = command.to_dict()
            cwd = params.get("cwd", cwd)
            blocking = params.get("blocking", blocking)
            command = params.get("command")
        if not self.allow_command_execution:
            logger.warning(
                "RunCommandTool.execute is disabled (allow_command_execution=False). "
                "It runs arbitrary shell commands via subprocess(shell=True) with no "
                "sandboxing; set allow_command_execution=True to opt in only for "
                "trusted environments.")
            disabled = CommandResult(
                thread_id=threading.get_ident(),
                status=CommandStatus.ERROR,
                stdout="",
                stderr=("RunCommandTool is disabled by default because it executes "
                        "arbitrary shell commands on the host without sandboxing. Set "
                        "`allow_command_execution: True` to opt in, and only do so in a "
                        "trusted, isolated environment."),
                start_time=time.time(),
            )
            disabled.end_time = disabled.start_time
            _command_results[disabled.thread_id] = disabled
            return disabled.message
        cwd = cwd or os.getcwd()
        try:
            blocking = parse_strict_bool(blocking, "blocking", default=True)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "status": CommandStatus.ERROR.value
            })
        return self._run_command(command, cwd, blocking)

    # Maximum time (seconds) to wait for the worker thread to register its
    # command result. Prevents indefinite blocking when the worker fails to
    # start (e.g. thread creation error or early exception before set()).
    _THREAD_STARTED_TIMEOUT = 10.0

    def _run_command(self, command: str, cwd: str, blocking: bool = True) -> str:
        result = CommandResult(
            thread_id=threading.get_ident(),
            status=CommandStatus.RUNNING,
            stdout="",
            stderr="",
            start_time=time.time(),
        )

        thread_started = threading.Event()
        thread_error: list = []  # captured from worker if it fails before set()

        def __run() -> None:
            try:
                result.thread_id = threading.get_ident()
                _command_results[result.thread_id] = result
                thread_started.set()
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
                thread_error.append(e)
                result.stderr = str(e)
                result.end_time = time.time()
                result.status = CommandStatus.ERROR

            _command_results[result.thread_id] = result

        if blocking:
            __run()
            return result.message

        # Non-blocking: spawn worker, wait with timeout for it to register.
        thread = threading.Thread(target=__run)
        thread.daemon = True
        thread.start()

        if not thread_started.wait(timeout=self._THREAD_STARTED_TIMEOUT):
            # Worker did not signal readiness in time; surface a clear error
            # instead of leaving the caller blocked forever.
            return json.dumps({
                "error": f"Command failed to start within {self._THREAD_STARTED_TIMEOUT}s",
                "status": CommandStatus.ERROR.value
            })

        if thread_error:
            return json.dumps({
                "error": f"Command thread failed to start: {thread_error[0]}",
                "status": CommandStatus.ERROR.value
            })

        # Return a minimal "started" acknowledgement. stdout/stderr/exit_code
        # are not yet populated; the caller should query CommandStatusTool with
        # thread_id to retrieve the final result.
        return json.dumps({
            "thread_id": result.thread_id,
            "status": CommandStatus.RUNNING.value,
            "started": True,
            "message": "Command started in non-blocking mode. Use command_status_tool with thread_id to query."
        })


def get_command_result(thread_id: int) -> Optional[CommandResult]:
    return _command_results.get(thread_id)
