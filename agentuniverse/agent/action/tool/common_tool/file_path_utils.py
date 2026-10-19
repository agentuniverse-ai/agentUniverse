# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os


def resolve_safe_path(file_path: str, base_dir: str = ".") -> str:
    """Resolve file_path and ensure it stays under base_dir."""
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("file_path must be a non-empty string")

    base = os.path.realpath(os.path.abspath(base_dir or "."))
    if os.path.isabs(file_path):
        resolved = os.path.realpath(file_path)
    else:
        resolved = os.path.realpath(os.path.join(base, file_path))

    try:
        common_path = os.path.commonpath([base, resolved])
    except ValueError as exc:
        raise ValueError(f"Path {file_path!r} escapes the allowed directory: {base}") from exc

    if os.path.normcase(common_path) != os.path.normcase(base):
        raise ValueError(f"Path {file_path!r} escapes the allowed directory: {base}")
    return resolved
