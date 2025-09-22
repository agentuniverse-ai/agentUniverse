#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/12 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: test_youtube_tool.py

import unittest
import os
from agentuniverse.agent.action.tool.common_tool.youtube_tool import YouTubeTool, Mode
from agentuniverse.agent.action.tool.tool import ToolInput

class YouTubeToolTest(unittest.TestCase):
    """
    Test cases for YouTubeTool class
    """
    def setUp(self) -> None:
        self.tool = YouTubeTool()
    
    def test_search_videos(self) -> None:
        tool_input = ToolInput({
            'mode': Mode.VIDEO_SEARCH.value,
            'input': 'machine learning'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != [])

    def test_analyze_channel(self) -> None:
        tool_input = ToolInput({
            'mode': Mode.CHANNEL_INFO.value,
            'input': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != {})

    def test_get_trending_videos_with_region(self) -> None:
        tool_input = ToolInput({
            'mode': Mode.TRENDING_VIDEOS.value,
            'input': 'US'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != [])

    def test_get_trending_videos(self) -> None:
        tool_input = ToolInput({
            'mode': Mode.TRENDING_VIDEOS.value
        })
        result = self.tool.execute(mode=tool_input.mode)
        self.assertTrue(result != [])

if __name__ == '__main__':
    unittest.main()