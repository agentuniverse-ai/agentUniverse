"""Channel uploads expose the video's publication date, not insertion date."""
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.tool.common_tool.youtube_tool import YouTubeTool

INSERTED = '2024-01-01T00:00:00Z'
PUBLISHED = '2024-02-01T00:00:00Z'


def service_for(pages):
    service = Mock()
    service.channels.return_value.list.return_value.execute.return_value = {'items': [{
        'snippet': {'title': 'Channel', 'description': 'Description'},
        'statistics': {'subscriberCount': '3', 'viewCount': '4', 'videoCount': '5'},
        'contentDetails': {'relatedPlaylists': {'uploads': 'upload-playlist'}},
    }]}
    service.playlistItems.return_value.list.return_value.execute.side_effect = pages
    return service


def item(identifier, details):
    return {'snippet': {'title': identifier, 'publishedAt': INSERTED},
            'contentDetails': {'videoId': identifier, **details}}


@pytest.mark.parametrize('details,expected', [
    ({'videoPublishedAt': PUBLISHED}, PUBLISHED),
    ({'videoPublishedAt': INSERTED}, INSERTED),
    ({}, INSERTED),
    ({'videoPublishedAt': None}, INSERTED),
    ({'videoPublishedAt': ''}, INSERTED),
])
def test_channel_video_publication_date_with_legacy_fallback(details, expected):
    service = service_for([{'items': [item('video', details)]}])
    result = YouTubeTool(service=service, api_key=None, max_results=1).execute(mode='channel_info', input='channel')
    assert result['latest_video_list'] == [{'id': 'video', 'title': 'video', 'published_at': expected}]
    assert result['name'] == 'Channel'
    assert result['subscriber_count'] == 3
    assert service.playlistItems.return_value.list.call_args.kwargs['part'] == 'snippet,contentDetails'


def test_multiple_pages_keep_order_and_per_video_dates():
    service = service_for([
        {'items': [item('first', {'videoPublishedAt': PUBLISHED})], 'nextPageToken': 'next'},
        {'items': [item('second', {})]},
    ])
    result = YouTubeTool(service=service, api_key=None, max_results=2).execute(mode='channel_info', input='channel')
    assert [video['id'] for video in result['latest_video_list']] == ['first', 'second']
    assert [video['published_at'] for video in result['latest_video_list']] == [PUBLISHED, INSERTED]
    calls = service.playlistItems.return_value.list.call_args_list
    assert len(calls) == 2
    assert calls[1].kwargs['pageToken'] == 'next'
    assert calls[1].kwargs['maxResults'] == 1
