"""YouTube request page sizes stay within the documented API limit."""

from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool.youtube_tool import YouTubeTool


@pytest.mark.parametrize("mode,limit,expected", [
    ("search", 75, 50), ("trending", 75, 50),
    ("search", 10, 10), ("trending", 10, 10),
    ("search", 50, 50), ("trending", 50, 50),
])
def test_single_page_modes_bound_api_request(mode, limit, expected):
    """Large result ceilings do not produce an invalid maxResults parameter."""
    service = Mock()
    service.search.return_value.list.return_value.execute.return_value = {"items": []}
    service.videos.return_value.list.return_value.execute.return_value = {"items": []}
    tool = YouTubeTool(service=service, api_key=None, max_results=limit)
    assert tool.execute(mode=mode, input="example") == []
    resource = service.search.return_value if mode == "search" else service.videos.return_value
    resource.list.assert_called_once()
    assert resource.list.call_args.kwargs["maxResults"] == expected
    assert tool.max_results == limit


@pytest.mark.parametrize("limit,expected_sizes", [(75, [50, 25]), (100, [50, 50]), (10, [10])])
def test_channel_pages_keep_total_limit(limit, expected_sizes):
    """Cap each page without reducing the requested total number of uploads."""
    service = Mock()
    service.channels.return_value.list.return_value.execute.return_value = {"items": [{
        "snippet": {"title": "Example"}, "statistics": {},
        "contentDetails": {"relatedPlaylists": {"uploads": "uploads"}},
    }]}
    calls = []

    def playlist_page(**kwargs):
        calls.append(kwargs)
        start = int(kwargs.get("pageToken") or 0)
        count = min(kwargs["maxResults"], 50)
        items = [{
            "contentDetails": {"videoId": str(index), "videoPublishedAt": "2023-12-01T00:00:00Z"},
            "snippet": {"title": str(index), "publishedAt": "2024-01-01T00:00:00Z"},
        } for index in range(start, start + count)]
        return Mock(execute=Mock(return_value={"items": items, "nextPageToken": str(start + count)}))

    service.playlistItems.return_value.list.side_effect = playlist_page
    result = YouTubeTool(service=service, api_key=None, max_results=limit).execute(
        mode="channel_info", input="channel",
    )
    assert len(result["latest_video_list"]) == limit
    assert [entry["id"] for entry in result["latest_video_list"]] == [str(i) for i in range(limit)]
    assert {entry["published_at"] for entry in result["latest_video_list"]} == {"2023-12-01T00:00:00Z"}
    assert [call["maxResults"] for call in calls] == expected_sizes
    assert [call["pageToken"] for call in calls] == [None] + [str(sum(expected_sizes[:i])) for i in range(1, len(calls))]
