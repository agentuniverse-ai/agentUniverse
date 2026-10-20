# !/usr/bin/env python3

# @Time    : 2025/3/22 19:15
# @Author  : hiro
# @Email   : hiromesh@qq.com
# @FileName: view_file_tool.py

import json
import os
from typing import Any

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

_START_LINE_NEGATIVE = "start_line must be greater than or equal to 0"
_END_LINE_NEGATIVE = "end_line must be greater than or equal to 0"
_START_AFTER_END = "start_line must be less than or equal to end_line"


class _InvalidLineNumber(TypeError, ValueError):
    """A line bound is not an integer, or not a canonical integer string."""

    def __init__(self, field_name: str, canonical: bool = False) -> None:
        detail = "must be a canonical integer string" if canonical else "must be an integer"
        super().__init__(f"{field_name} {detail}")


class ViewFileTool(Tool):
    """Read a UTF-8 text file, optionally limited to a line range.

    ``start_line`` and ``end_line`` use zero-based line positions and the end
    bound is exclusive, matching Python slice semantics. A request for lines
    ``1`` to ``3`` therefore returns the second and third line. The response
    reports the inclusive last line that was returned, so that same request
    returns ``start_line=1`` and ``end_line=2``.
    """

    base_dir: str = "."

    @staticmethod
    def _error(message: str, file_path: Any = None) -> str:
        """Build the JSON error payload used by every failure path."""
        payload = {
            "error": message,
            "status": "error",
        }
        if file_path is not None:
            payload["file_path"] = file_path
        return json.dumps(payload)

    @staticmethod
    def _normalize_line_number(value: Any, field_name: str, allow_none: bool = False) -> int | None:
        """Parse a line bound and reject values that cannot be a line number.

        Booleans are rejected even though ``bool`` is a subclass of ``int``,
        and string forms have to be canonical (``"01"`` and ``" 1"`` are not
        accepted). Negative values are handled by ``_validate_line_bounds`` so
        the error can name the offending field.
        """
        if value is None and allow_none:
            return None
        if isinstance(value, bool):
            raise _InvalidLineNumber(field_name)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                parsed_value = int(value)
            except ValueError as exc:
                raise _InvalidLineNumber(field_name) from exc
            if str(parsed_value) != value:
                raise _InvalidLineNumber(field_name, canonical=True)
            return parsed_value
        raise _InvalidLineNumber(field_name)

    @staticmethod
    def _validate_line_bounds(start_line: int, end_line: int | None) -> None:
        """Reject line bounds that cannot describe a real range.

        A negative bound used to be clamped with ``max(0, start_line)`` or fed
        straight into a slice. ``start_line=-1`` returned the whole file, and
        ``start_line=-2, end_line=-1`` returned every line except the last one,
        which is a silent wrong answer rather than an error.
        """
        if start_line < 0:
            raise ValueError(_START_LINE_NEGATIVE)
        if end_line is not None and end_line < 0:
            raise ValueError(_END_LINE_NEGATIVE)
        if end_line is not None and start_line > end_line:
            raise ValueError(_START_AFTER_END)

    @staticmethod
    def _read_lines(file_path: str, start_line: int, end_line: int | None) -> tuple[str, int]:
        """Read the requested lines without keeping the whole file in memory.

        The previous implementation called ``readlines()`` and then sliced the
        resulting list. That allocated one string per line for every request,
        including a one-line preview of a multi-gigabyte log. Iterating over the
        file and retaining only the requested lines keeps memory proportional
        to the requested range while still counting every line for the
        ``total_lines`` field in the response.
        """
        selected_lines: list[str] = []
        total_lines = 0
        with open(file_path, encoding="utf-8") as file:
            for line_number, line in enumerate(file):
                total_lines = line_number + 1
                if line_number < start_line:
                    continue
                if end_line is not None and line_number >= end_line:
                    continue
                selected_lines.append(line)
        return "".join(selected_lines), total_lines

    def execute(
        self,
        file_path: str | ToolInput,
        start_line: int = 0,
        end_line: int | None = None,
    ) -> str:
        if isinstance(file_path, ToolInput):
            params = file_path.to_dict()
            start_line = params.get("start_line", start_line)
            end_line = params.get("end_line", end_line)
            file_path = params.get("file_path")

        try:
            start_line = self._normalize_line_number(start_line, "start_line")
            end_line = self._normalize_line_number(end_line, "end_line", allow_none=True)
            self._validate_line_bounds(start_line, end_line)
            safe_file_path = resolve_safe_path(file_path, self.base_dir)
        except ValueError as exc:
            return self._error(str(exc), file_path)

        if not safe_file_path or not os.path.isfile(safe_file_path):
            return self._error(f"File not found: {safe_file_path}")

        try:
            content, total_lines = self._read_lines(safe_file_path, start_line, end_line)
        except UnicodeDecodeError as exc:
            return self._error(
                f"File is not valid UTF-8 text: {exc.reason} at byte offset {exc.start}",
                safe_file_path,
            )
        except OSError as exc:
            return self._error(f"Failed to read file: {exc}", safe_file_path)

        last_line = min(end_line, total_lines) if end_line is not None else total_lines
        return json.dumps(
            {
                "file_path": safe_file_path,
                "content": content,
                "start_line": start_line,
                "end_line": last_line - 1 if last_line > 0 else 0,
                "total_lines": total_lines,
                "status": "success",
            }
        )
