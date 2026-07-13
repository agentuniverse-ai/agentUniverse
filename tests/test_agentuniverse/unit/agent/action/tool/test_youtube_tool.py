#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/7/12 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: test_youtube_tool.py

import unittest
from agentuniverse.agent.action.tool.common_tool.youtube_tool import YouTubeTool, Mode
from agentuniverse.agent.action.tool.tool import ToolInput


class FakeRequest:
    def __init__(self, response):
        self.response = response

    def execute(self):
        return self.response


class FakeSearchResource:
    def list(self, **kwargs):
        return FakeRequest({
            "items": [{"id": {"videoId": "video-1"}}]
        })


class FakeVideosResource:
    def list(self, **kwargs):
        if kwargs.get("chart") == "mostPopular":
            return FakeRequest({
                "items": [{
                    "id": "trending-1",
                    "snippet": {
                        "title": "Trending video",
                        "channelTitle": "Test channel",
                        "publishedAt": "2026-07-12T00:00:00Z",
                    },
                    "statistics": {
                        "viewCount": "100",
                        "likeCount": "10",
                        "commentCount": "1",
                    },
                    "contentDetails": {"duration": "PT1M30S"},
                }]
            })
        return FakeRequest({
            "items": [{
                "id": "video-1",
                "snippet": {"title": "Machine learning video"},
                "statistics": {
                    "viewCount": "100",
                    "likeCount": "10",
                    "commentCount": "1",
                },
                "contentDetails": {"duration": "PT2M"},
            }]
        })


class FakeChannelsResource:
    def list(self, **kwargs):
        return FakeRequest({
            "items": [{
                "snippet": {
                    "title": "Google Developers",
                    "description": "Developer videos",
                },
                "statistics": {
                    "subscriberCount": "1000",
                    "viewCount": "2000",
                    "videoCount": "3",
                },
                "contentDetails": {
                    "relatedPlaylists": {"uploads": "uploads-playlist"}
                },
            }]
        })


class FakePlaylistItemsResource:
    def list(self, **kwargs):
        return FakeRequest({
            "items": [{
                "contentDetails": {"videoId": "upload-1"},
                "snippet": {
                    "title": "Latest upload",
                    "publishedAt": "2026-07-12T00:00:00Z",
                },
            }]
        })


class FakeYouTubeService:
    def search(self):
        return FakeSearchResource()

    def videos(self):
        return FakeVideosResource()

    def channels(self):
        return FakeChannelsResource()

    def playlistItems(self):
        return FakePlaylistItemsResource()


class YouTubeToolTest(unittest.TestCase):
    """
    Test cases for YouTubeTool class
    """
    def setUp(self) -> None:
        self.tool = YouTubeTool(service=FakeYouTubeService(), api_key="test-key")
    
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
