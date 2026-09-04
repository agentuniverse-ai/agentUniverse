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
    """Minimal fake mimicking a googleapiclient HTTP request object."""
    def __init__(self, response):
        """Store the canned response returned by execute()."""
        self.response = response

    def execute(self):
        """Return the canned API response stored at construction."""
        return self.response


class FakeSearchResource:
    """Fake for the youtube search resource."""
    def list(self, **kwargs):
        """Return a FakeRequest whose payload lists one video search result."""
        return FakeRequest({
            "items": [{"id": {"videoId": "video-1"}}]
        })


class FakeVideosResource:
    """Fake for the youtube videos resource."""
    def list(self, **kwargs):
        """Return a FakeRequest with trending or generic video items depending on the chart kwarg."""
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
    """Fake for the youtube channels resource."""
    def list(self, **kwargs):
        """Return a FakeRequest whose payload carries one channel with snippet, statistics, and contentDetails."""
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
    """Fake for the youtube playlistItems resource."""
    def list(self, **kwargs):
        """Return a FakeRequest whose payload lists a single upload item."""
        return FakeRequest({
            "items": [{
                "contentDetails": {"videoId": "upload-1"},
                "snippet": {
                    "title": "Latest upload",
                    "publishedAt": "2026-07-12T00:00:00Z",
                },
            }]
        })


class FakePagedPlaylistItemsResource:
    """Fake playlistItems resource that pages two uploads per call and records requested maxResults."""
    def __init__(self):
        """Initialize the paging counters and the recorded maxResults list."""
        self.calls = 0
        self.max_results_values = []

    def list(self, **kwargs):
        """Return the next page of upload items, recording the requested maxResults kwarg."""
        self.calls += 1
        self.max_results_values.append(kwargs.get("maxResults"))
        start = (self.calls - 1) * 2
        items = [
            {
                "contentDetails": {"videoId": f"upload-{start + index}"},
                "snippet": {
                    "title": f"Upload {start + index}",
                    "publishedAt": "2026-07-12T00:00:00Z",
                },
            }
            for index in range(1, 3)
        ]
        response = {"items": items}
        if self.calls == 1:
            response["nextPageToken"] = "next-page"
        return FakeRequest(response)


class FakeYouTubeService:
    """Fake of a googleapiclient YouTube service exposing the resource accessors used by the tool."""
    def __init__(self, playlist_items_resource=None):
        """Store the playlistItems resource, defaulting to a fresh FakePlaylistItemsResource."""
        self.playlist_items_resource = playlist_items_resource or FakePlaylistItemsResource()

    def search(self):
        """Return a FakeSearchResource instance."""
        return FakeSearchResource()

    def videos(self):
        """Return a FakeVideosResource instance."""
        return FakeVideosResource()

    def channels(self):
        """Return a FakeChannelsResource instance."""
        return FakeChannelsResource()

    def playlistItems(self):
        """Return the configured playlistItems resource."""
        return self.playlist_items_resource


class YouTubeToolTest(unittest.TestCase):
    """
    Test cases for YouTubeTool class
    """
    def setUp(self) -> None:
        """Build a YouTubeTool backed by the fake service before each test."""
        self.tool = YouTubeTool(service=FakeYouTubeService(), api_key="test-key")
    
    def test_search_videos(self) -> None:
        """Verify video search mode returns a non-empty result list."""
        tool_input = ToolInput({
            'mode': Mode.VIDEO_SEARCH.value,
            'input': 'machine learning'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != [])

    def test_analyze_channel(self) -> None:
        """Verify channel info mode returns a non-empty result dict."""
        tool_input = ToolInput({
            'mode': Mode.CHANNEL_INFO.value,
            'input': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != {})

    def test_channel_info_limits_latest_videos_to_max_results(self) -> None:
        """Verify channel info fetches latest videos in pages up to max_results."""
        playlist_items_resource = FakePagedPlaylistItemsResource()
        tool = YouTubeTool(
            service=FakeYouTubeService(playlist_items_resource),
            api_key="test-key",
            max_results=3
        )

        result = tool.execute(Mode.CHANNEL_INFO.value, 'UC_x5XG1OV2P6uZZ5FSM9Ttw')

        self.assertEqual(len(result['latest_video_list']), 3)
        self.assertEqual(playlist_items_resource.max_results_values, [3, 1])

    def test_get_trending_videos_with_region(self) -> None:
        """Verify trending videos mode works when a region code is supplied."""
        tool_input = ToolInput({
            'mode': Mode.TRENDING_VIDEOS.value,
            'input': 'US'
        })
        result = self.tool.execute(tool_input.mode, tool_input.input)
        self.assertTrue(result != [])

    def test_get_trending_videos(self) -> None:
        """Verify trending videos mode works without a region code."""
        tool_input = ToolInput({
            'mode': Mode.TRENDING_VIDEOS.value
        })
        result = self.tool.execute(mode=tool_input.mode)
        self.assertTrue(result != [])

    def test_parse_duration_with_day_component(self) -> None:
        """Verify parse_duration converts an ISO-8601 duration with days to seconds."""
        self.assertEqual(self.tool.parse_duration('P1DT2H3M4S'), 93784)

    def test_parse_duration_rejects_partial_trailing_text(self) -> None:
        """Verify parse_duration returns zero for malformed trailing text."""
        self.assertEqual(self.tool.parse_duration('PT1Mbad'), 0)

    def test_parse_stat_count_handles_missing_or_malformed_values(self) -> None:
        """Verify _parse_stat_count handles missing or malformed count values."""
        self.assertEqual(self.tool._parse_stat_count("123"), 123)
        self.assertEqual(self.tool._parse_stat_count(None), 0)
        self.assertEqual(self.tool._parse_stat_count(""), 0)
        self.assertEqual(self.tool._parse_stat_count("hidden"), 0)

if __name__ == '__main__':
    unittest.main()
