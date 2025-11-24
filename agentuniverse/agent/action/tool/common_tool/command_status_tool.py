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
    """Tool for checking the status of running commands.
    
    This tool allows checking the status and results of commands executed by RunCommandTool.
    It retrieves command results by thread ID and returns formatted status information.
    """
    def execute(self, thread_id: int) -> str:
        """Check the status of a command by thread ID.
        
        Args:
            thread_id (int): Thread ID of the command to check
            
        Returns:
            str: JSON string containing command status and results, or error message if not found
        """
        if isinstance(thread_id, str) and thread_id.isdigit():
            thread_id = int(thread_id)

        result = get_command_result(thread_id)

        if result is None:
            return json.dumps({
                "error": f"No command found with thread_id: {thread_id}",
                "status": "not_found"
            })
        return result.message
