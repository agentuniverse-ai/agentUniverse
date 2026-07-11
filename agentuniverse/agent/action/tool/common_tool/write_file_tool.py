# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: write_file_tool.py

import os
import json
from typing import Optional

from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class WriteFileTool(Tool):
    """Tool that writes content to a file.

    Writes are confined to a workspace directory (issue #571) so that a
    prompt-injected agent cannot overwrite arbitrary host files such as
    ``~/.bashrc`` or ``.env``.

    Attributes:
        base_dir (Optional[str]): Directory used as the write workspace. When
            unset (the default) the tool confines writes to the current working
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
        """Resolve ``file_path`` and confine it to the write workspace.

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
                content: str = '',
                append: bool = False) -> str:
        try:
            safe_path = self._resolve_path(file_path)
        except ValueError as e:
            return json.dumps({
                "error": str(e),
                "file_path": file_path,
                "status": "error"
            })

        directory = os.path.dirname(safe_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                return json.dumps({
                    "error": f"Failed to create directory: {str(e)}",
                    "file_path": safe_path,
                    "status": "error"
                })

        try:
            mode = 'a' if append else 'w'

            with open(safe_path, mode, encoding='utf-8') as file:
                file.write(content)
            file_size = os.path.getsize(safe_path)
            return json.dumps({
                "file_path": safe_path,
                "bytes_written": len(content.encode('utf-8')),
                "file_size": file_size,
                "append_mode": append,
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "file_path": safe_path,
                "status": "error"
            })
