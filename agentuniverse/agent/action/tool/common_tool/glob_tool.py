# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: glob_tool.py

import os
import json
from pathlib import Path

from agentuniverse.agent.action.tool.tool import Tool

# Directories to exclude from glob results
_EXCLUDED_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', '.tox', '.mypy_cache', '.pytest_cache'}


class GlobTool(Tool):
    """Fast file pattern matching using glob patterns."""

    def execute(self, pattern: str, path: str = None) -> str:
        try:
            base_path = Path(path) if path else Path(os.getcwd())

            if not base_path.is_dir():
                return json.dumps({
                    "error": f"Directory not found: {base_path}",
                    "status": "error"
                })

            matched = []
            for p in base_path.glob(pattern):
                # Skip files inside excluded directories
                if any(part in _EXCLUDED_DIRS for part in p.parts):
                    continue
                if p.is_file():
                    matched.append(p)

            # Sort by modification time, newest first
            matched.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            results = [str(p) for p in matched]

            return json.dumps({
                "files": results,
                "count": len(results),
                "pattern": pattern,
                "path": str(base_path),
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "status": "error"
            })
