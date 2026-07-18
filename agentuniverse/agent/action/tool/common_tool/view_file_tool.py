# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: view_file_tool.py

import os
import json

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path


class ViewFileTool(Tool):
    base_dir: str = "."

    @staticmethod
    def _normalize_line_number(value, field_name: str, allow_none: bool = False):
        if value is None and allow_none:
            return None
        if isinstance(value, bool):
            raise ValueError(f"{field_name} must be an integer")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                parsed_value = int(value)
            except ValueError as exc:
                raise ValueError(f"{field_name} must be an integer") from exc
            if str(parsed_value) != value:
                raise ValueError(f"{field_name} must be a canonical integer string")
            return parsed_value
        raise ValueError(f"{field_name} must be an integer")

    def execute(self,
                file_path: str | ToolInput,
                start_line: int = 0,
                end_line: int = None
                ) -> str:
        if isinstance(file_path, ToolInput):
            params = file_path.to_dict()
            start_line = params.get('start_line', start_line)
            end_line = params.get('end_line', end_line)
            file_path = params.get('file_path')

        try:
            start_line = self._normalize_line_number(start_line, "start_line")
            end_line = self._normalize_line_number(end_line, "end_line", allow_none=True)
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
        if not file_path or not os.path.isfile(file_path):
            return json.dumps({
                "error": f"File not found: {file_path}",
                "status": "error"
            })

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                all_lines = file.readlines()
            if end_line is None:
                end_line = len(all_lines)
            start_line = max(0, start_line)
            end_line = min(len(all_lines), end_line)

            content_lines = all_lines[start_line:end_line]
            content = ''.join(content_lines)
            return json.dumps({
                "file_path": file_path,
                "content": content,
                "start_line": start_line,
                "end_line": end_line - 1 if end_line > 0 else 0,
                "total_lines": len(all_lines),
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })
