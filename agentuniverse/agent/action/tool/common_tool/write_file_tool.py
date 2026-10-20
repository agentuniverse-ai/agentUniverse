# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: write_file_tool.py

import os
import json
import tempfile

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.common_tool.tool_input_utils import parse_strict_bool


class WriteFileTool(Tool):
    base_dir: str = "."

    def execute(self,
                file_path: str | ToolInput,
                content: str = '',
                append: bool = False) -> str:
        if isinstance(file_path, ToolInput):
            params = file_path.to_dict()
            content = params.get('content', content)
            append = params.get('append', append)
            file_path = params.get('file_path')
        if not isinstance(content, str):
            return json.dumps({
                "error": "content must be a string",
                "file_path": file_path,
                "status": "error"
            })

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
            if append:
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write(content)
            else:
                # Write beside the destination and replace it only after the
                # complete UTF-8 write succeeds.  Opening the destination in
                # ``w`` mode first can destroy an existing file when encoding
                # or I/O fails halfway through the operation.
                temporary_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode='w',
                        encoding='utf-8',
                        dir=directory or None,
                        prefix=f'.{os.path.basename(file_path)}.',
                        suffix='.tmp',
                        delete=False,
                    ) as temporary_file:
                        temporary_path = temporary_file.name
                        temporary_file.write(content)
                        temporary_file.flush()
                        os.fsync(temporary_file.fileno())
                    os.replace(temporary_path, file_path)
                    temporary_path = None
                finally:
                    if temporary_path and os.path.exists(temporary_path):
                        os.unlink(temporary_path)
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
