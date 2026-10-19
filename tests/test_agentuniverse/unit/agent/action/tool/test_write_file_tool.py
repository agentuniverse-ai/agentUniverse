# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_write_file_tool.py
"""Unit tests for WriteFileTool."""

import json
import os

import pytest

from agentuniverse.agent.action.tool.common_tool.write_file_tool import WriteFileTool
from agentuniverse.agent.action.tool.tool import ToolInput


class TestWriteFileTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return WriteFileTool(base_dir=str(tmp_path))

    def test_write_new_file(self, tool, tmp_path):
        result = json.loads(tool.execute('out.txt', content='hello'))
        assert result['status'] == 'success'
        assert (tmp_path / 'out.txt').read_text(encoding='utf-8') == 'hello'

    def test_append_mode(self, tool, tmp_path):
        tool.execute('log.txt', content='first\n')
        result = json.loads(tool.execute('log.txt', content='second\n', append=True))
        assert result['status'] == 'success'
        assert result['append_mode'] is True
        assert (tmp_path / 'log.txt').read_text(encoding='utf-8') == 'first\nsecond\n'

    def test_append_string_truthy(self, tool, tmp_path):
        tool.execute('a.txt', content='x')
        result = json.loads(tool.execute('a.txt', content='y', append='yes'))
        assert result['status'] == 'success'
        assert (tmp_path / 'a.txt').read_text(encoding='utf-8') == 'xy'

    def test_invalid_append_value(self, tool):
        result = json.loads(tool.execute('x.txt', content='y', append='maybe'))
        assert result['status'] == 'error'

    def test_creates_missing_directory(self, tool, tmp_path):
        result = json.loads(tool.execute(os.path.join('sub', 'dir', 'f.txt'), content='z'))
        assert result['status'] == 'success'
        assert (tmp_path / 'sub' / 'dir' / 'f.txt').read_text(encoding='utf-8') == 'z'

    def test_escape_path_rejected(self, tool):
        result = json.loads(tool.execute('../evil.txt', content='x'))
        assert result['status'] == 'error'
        assert 'escapes' in result['error']

    def test_tool_input_style(self, tool, tmp_path):
        tool_input = ToolInput({'file_path': 'ti.txt', 'content': 'data'})
        result = json.loads(tool.execute(tool_input))
        assert result['status'] == 'success'
        assert (tmp_path / 'ti.txt').read_text(encoding='utf-8') == 'data'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
