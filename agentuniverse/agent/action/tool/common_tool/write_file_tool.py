# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: write_file_tool.py

import os
import json

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.common_tool.tool_input_utils import parse_strict_bool


class WriteFileTool(Tool):
    """Tool that writes text content to a file inside the configured base directory.
    """
    base_dir: str = "."

    def execute(self,
                file_path: str | ToolInput,
                content: str = '',
                append: bool = False) -> str:
        """Write the given content to the target file, optionally appending, and return a JSON status string.

        Args:
            file_path(str | ToolInput): The file path, or a ToolInput holding it.
            content(str): The text content to write.
            append(bool): Whether to append to the file instead of overwriting.

        Returns:
            str: A JSON string with the write result and status.
        """
        if isinstance(file_path, ToolInput):
            params = file_path.to_dict()
            content = params.get('content', content)
            append = params.get('append', append)
            file_path = params.get('file_path')
        try:
            append = parse_strict_bool(append, "append", default=False)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })

        try:
            safe_file_path = resolve_safe_path(file_path, self.base_dir)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })

        file_path = safe_file_path
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to create directory: {str(e)}",
                    "file_path": file_path,
                    "status": "error"
                })

        try:
            mode = 'a' if append else 'w'

            with open(file_path, mode, encoding='utf-8') as file:
                file.write(content)
            file_size = os.path.getsize(file_path)
            return json.dumps({
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "file_size": file_size,
                "append_mode": append,
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })
