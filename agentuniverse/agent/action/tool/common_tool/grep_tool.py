# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/15 10:00
# @FileName: grep_tool.py

import os
import re
import json
import fnmatch

from agentuniverse.agent.action.tool.tool import Tool

# Directories to skip during traversal
_EXCLUDED_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', '.tox', '.mypy_cache', '.pytest_cache'}

# Mapping from short type names to glob patterns
_TYPE_GLOB_MAP = {
    'py': '*.py', 'js': '*.js', 'ts': '*.ts', 'tsx': '*.tsx', 'jsx': '*.jsx',
    'java': '*.java', 'go': '*.go', 'rs': '*.rs', 'rust': '*.rs',
    'c': '*.c', 'cpp': '*.cpp', 'h': '*.h', 'hpp': '*.hpp',
    'rb': '*.rb', 'php': '*.php', 'swift': '*.swift', 'kt': '*.kt',
    'scala': '*.scala', 'sh': '*.sh', 'bash': '*.sh',
    'yaml': '*.yaml', 'yml': '*.yml', 'json': '*.json', 'toml': '*.toml',
    'xml': '*.xml', 'html': '*.html', 'css': '*.css', 'md': '*.md',
    'sql': '*.sql', 'r': '*.r', 'lua': '*.lua',
}


class GrepTool(Tool):
    """Search file contents using regular expressions."""

    def execute(self, pattern: str, path: str = None, glob: str = None,
                type: str = None, output_mode: str = "files_with_matches",
                context: int = 0, case_insensitive: bool = False,
                head_limit: int = 0) -> str:
        try:
            base_path = path or os.getcwd()

            if not os.path.isdir(base_path):
                return json.dumps({
                    "error": f"Directory not found: {base_path}",
                    "status": "error"
                })

            # Determine file glob filter
            file_glob = None
            if glob:
                file_glob = glob
            elif type and type in _TYPE_GLOB_MAP:
                file_glob = _TYPE_GLOB_MAP[type]

            flags = re.IGNORECASE if case_insensitive else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return json.dumps({
                    "error": f"Invalid regex pattern: {e}",
                    "status": "error"
                })

            results = []
            entry_count = 0

            for dirpath, dirnames, filenames in os.walk(base_path):
                # Prune excluded directories
                dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIRS]

                for filename in filenames:
                    if file_glob and not fnmatch.fnmatch(filename, file_glob):
                        continue

                    filepath = os.path.join(dirpath, filename)

                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                    except (OSError, IOError):
                        continue

                    matching_line_indices = []
                    for i, line in enumerate(lines):
                        if regex.search(line):
                            matching_line_indices.append(i)

                    if not matching_line_indices:
                        continue

                    if output_mode == "files_with_matches":
                        results.append(filepath)
                        entry_count += 1
                        if 0 < head_limit <= entry_count:
                            break

                    elif output_mode == "count":
                        results.append({
                            "file": filepath,
                            "count": len(matching_line_indices)
                        })
                        entry_count += 1
                        if 0 < head_limit <= entry_count:
                            break

                    elif output_mode == "content":
                        file_matches = []
                        for idx in matching_line_indices:
                            start = max(0, idx - context)
                            end = min(len(lines), idx + context + 1)
                            snippet_lines = []
                            for li in range(start, end):
                                snippet_lines.append({
                                    "line_number": li + 1,
                                    "content": lines[li].rstrip('\n\r'),
                                    "is_match": li in matching_line_indices
                                })
                            file_matches.append(snippet_lines)
                            entry_count += 1
                            if 0 < head_limit <= entry_count:
                                break

                        results.append({
                            "file": filepath,
                            "matches": file_matches
                        })

                    if 0 < head_limit <= entry_count:
                        break
                if 0 < head_limit <= entry_count:
                    break

            return json.dumps({
                "results": results,
                "pattern": pattern,
                "output_mode": output_mode,
                "status": "success"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "status": "error"
            })
