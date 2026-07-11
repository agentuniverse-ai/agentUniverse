# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: view_file_tool.py

import os
import json
from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class ViewFileTool(Tool):
    """Tool that reads the content of a file.

    Reads are confined to a workspace directory (issue #571) so that a
    prompt-injected agent cannot exfiltrate arbitrary host files such as
    ``~/.ssh/authorized_keys`` or ``/etc/shadow``.

    Attributes:
        base_dir (Optional[str]): Directory used as the read workspace. When
            unset (the default) the tool confines reads to the current working
            directory, so confinement is on out of the box. An integrator can
            override the workspace from the tool yaml, e.g.
            ``base_dir: /var/au_workspace``. Any ``file_path`` that resolves
            outside the workspace -- via an absolute path, a ``..`` traversal,
            or a symlink -- is rejected before the file is opened.

    Note:
        Path resolution uses ``os.path.realpath``; confinement is therefore
        enforced at resolution time. For fully untrusted input, also run the
        tool in a restricted subprocess or container.
    """
    base_dir: Optional[str] = None

    def _resolve_path(self, file_path: str) -> str:
        """Resolve ``file_path`` and confine it to the read workspace.

        The workspace is ``base_dir`` when it is set, otherwise the current
        working directory. ``file_path`` is resolved with
        ``os.path.realpath`` so that ``..`` segments and symlinks cannot
        escape the workspace.

        Args:
            file_path: The path requested by the caller (relative or absolute).

        Returns:
            The resolved, workspace-confined absolute path.

        Raises:
            ValueError: If ``file_path`` resolves outside the workspace.
        """
        base = self.base_dir if self.base_dir else os.getcwd()
        base = os.path.realpath(base)
        resolved = os.path.realpath(os.path.join(base, file_path))
        if resolved != base and not resolved.startswith(base + os.sep):
            raise ValueError(
                f"file_path '{file_path}' resolves outside of the allowed "
                f"workspace '{base}'")
        return resolved

    def execute(self,
                file_path: str,
                start_line: int = 0,
                end_line: int = None
                ) -> str:
        try:
            safe_path = self._resolve_path(file_path)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })

        if not safe_path or not os.path.isfile(safe_path):
            return json.dumps({
                "error": f"File not found: {file_path}",
                "status": "error"
            })

        try:
            with open(safe_path, 'r', encoding='utf-8') as file:
                all_lines = file.readlines()
            if end_line is None:
                end_line = len(all_lines)
            start_line = max(0, start_line)
            end_line = min(len(all_lines), end_line)

            content_lines = all_lines[start_line:end_line]
            content = ''.join(content_lines)
            return json.dumps({
                "file_path": safe_path,
                "content": content,
                "start_line": start_line,
                "end_line": end_line - 1 if end_line > 0 else 0,
                "total_lines": len(all_lines),
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "file_path": safe_path,
                "status": "error"
            })
