# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 18:00
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: command_status_tool.py

import json
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.common_tool.run_command_tool import get_command_result


class CommandStatusTool(Tool):
    """Tool that returns the status message of a previously launched command thread."""

    @staticmethod
    def _normalize_thread_id(thread_id):
        """Normalize a thread id value into an int.

        Args:
            thread_id: The raw thread id.

        Returns:
            int: The normalized thread id.

        Raises:
            ValueError: If the value is not an integer-like value.
        """
        if isinstance(thread_id, bool):
            raise ValueError("thread_id must be an integer")
        if isinstance(thread_id, int):
            return thread_id
        if isinstance(thread_id, str) and thread_id.isdigit():
            return int(thread_id)
        raise ValueError("thread_id must be an integer")

    def execute(self, thread_id: int | ToolInput) -> str:
        """Return the status message of the command with the given thread id as a JSON string.

        Args:
            thread_id(int | ToolInput): The thread id, or a ToolInput holding it.

        Returns:
            str: A JSON string with the command status.
        """
        if isinstance(thread_id, ToolInput):
            thread_id = thread_id.get_data("thread_id")
        try:
            thread_id = self._normalize_thread_id(thread_id)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "status": "error"
            })

        result = get_command_result(thread_id)

        if result is None:
            return json.dumps({
                "error": f"No command found with thread_id: {thread_id}",
                "status": "not_found"
            })
        return result.message
