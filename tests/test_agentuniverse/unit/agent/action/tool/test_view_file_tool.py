# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_view_file_tool.py
"""Unit tests for ViewFileTool."""

import json

import pytest

from agentuniverse.agent.action.tool.common_tool.view_file_tool import ViewFileTool
from agentuniverse.agent.action.tool.tool import ToolInput


class TestViewFileTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ViewFileTool(base_dir=str(tmp_path))

    @pytest.fixture
    def sample(self, tmp_path):
        f = tmp_path / 'sample.txt'
        f.write_text('line1\nline2\nline3\n', encoding='utf-8')
        return f.name

    def test_normalize_line_number(self):
        assert ViewFileTool._normalize_line_number('3', 'l') == 3
        assert ViewFileTool._normalize_line_number(2, 'l') == 2
        assert ViewFileTool._normalize_line_number(None, 'l', allow_none=True) is None
        with pytest.raises(ValueError):
            ViewFileTool._normalize_line_number('01', 'l')
        with pytest.raises(ValueError):
            ViewFileTool._normalize_line_number(True, 'l')

    def test_view_partial_lines(self, tool, sample):
        result = json.loads(tool.execute(sample, start_line=1, end_line=3))
        assert result['status'] == 'success'
        assert result['content'] == 'line2\nline3\n'

    def test_view_full_file(self, tool, sample):
        result = json.loads(tool.execute(sample))
        assert result['status'] == 'success'
        assert result['content'] == 'line1\nline2\nline3\n'
        assert result['total_lines'] == 3

    def test_view_missing_file(self, tool, tmp_path):
        result = json.loads(tool.execute('missing.txt'))
        assert result['status'] == 'error'
        assert 'File not found' in result['error']

    def test_escape_path_rejected(self, tool):
        result = json.loads(tool.execute('../outside.txt'))
        assert result['status'] == 'error'
        assert 'escapes' in result['error']

    def test_tool_input_style(self, tool, sample):
        tool_input = ToolInput({'file_path': sample, 'start_line': 2, 'end_line': 3})
        result = json.loads(tool.execute(tool_input))
        assert result['status'] == 'success'
        assert result['content'] == 'line3\n'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
