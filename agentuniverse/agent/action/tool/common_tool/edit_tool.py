# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: edit_tool.py

import os
import json

from agentuniverse.agent.action.tool.tool import Tool


class EditTool(Tool):
    """Perform exact string replacements in files."""

    def execute(self, file_path: str, old_string: str, new_string: str,
                replace_all: bool = False) -> str:
        if not file_path or not os.path.isfile(file_path):
            return json.dumps({
                "error": f"File not found: {file_path}",
                "status": "error"
            })

        if old_string == new_string:
            return json.dumps({
                "error": "old_string and new_string are identical",
                "status": "error"
            })

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            count = content.count(old_string)

            if count == 0:
                return json.dumps({
                    "error": "old_string not found in file",
                    "file_path": file_path,
                    "status": "error"
                })

            if not replace_all and count > 1:
                return json.dumps({
                    "error": f"old_string is not unique in file (found {count} occurrences). "
                             f"Provide more context to make it unique, or set replace_all=true.",
                    "file_path": file_path,
                    "occurrences": count,
                    "status": "error"
                })

            if replace_all:
                new_content = content.replace(old_string, new_string)
                replacements_made = count
            else:
                new_content = content.replace(old_string, new_string, 1)
                replacements_made = 1

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return json.dumps({
                "file_path": file_path,
                "replacements_made": replacements_made,
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })
