# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: write_file_tool.py

import os
import json

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class WriteFileTool(Tool):
    def execute(self,
                file_path: str,
                content: str = '',
                append: bool = False) -> str:
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
