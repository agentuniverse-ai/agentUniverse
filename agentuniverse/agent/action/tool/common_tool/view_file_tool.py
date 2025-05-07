# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: view_file_tool.py

import os
import json

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class ViewFileTool(Tool):
    def execute(self,
                file_path: str,
                start_line: int = 0,
                end_line: int = None
                ) -> str:
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
