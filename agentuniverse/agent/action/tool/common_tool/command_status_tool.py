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
    @staticmethod
    def _normalize_thread_id(thread_id):
        if isinstance(thread_id, bool):
            raise ValueError("thread_id must be an integer")
        if isinstance(thread_id, int):
            return thread_id
        if isinstance(thread_id, str) and thread_id.isdigit():
            return int(thread_id)
        raise ValueError("thread_id must be an integer")

    def execute(self, thread_id: int | ToolInput) -> str:
        """Return the latest result for a background command thread.

        Args:
            thread_id: Integer thread identifier or a legacy ``ToolInput``.

        Returns:
            The command result message, or a JSON validation/not-found response.
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
