#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/7/12 23:00
# @Author  : xmhu2001
# @Email   : xmhu2001@qq.com
# @FileName: youtube_tool.py

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.retry import retry
from agentuniverse.base.util.env_util import get_from_env
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

service_name = "youtube"
api_version = "v3"

class Mode(Enum):
    VIDEO_SEARCH = "search" 
    TRENDING_VIDEOS = "trending"
    CHANNEL_INFO = "channel_info" 

class YouTubeTool(Tool):

    service: Optional[Any] = None
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("YOUTUBE_API_KEY"))
    max_results: int = Field(10, description="Maximum video results to return")

    def _initialize_service(self):
        if not self.api_key:
            raise ValueError("YouTube API key not provided, please set the YOUTUBE_API_KEY environment variable.")
        if self.service is None:
            self.service = build(service_name, api_version, developerKey=self.api_key)
        return self.service

    def parse_duration(self, duration_str):
        """Converts ISO 8601 duration format to seconds"""
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
        if not match:
            return 0
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0
        return hours * 3600 + minutes * 60 + seconds

    @retry(3, 1.0)
    def _search_videos(self, query: str) -> List[Dict]:
        try:         
            search_response = self.service.search().list(
                q=query,
                part='id',
                type='video',
                maxResults=self.max_results
            ).execute()

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            if not video_ids:
                return []

            video_response = self.service.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics,contentDetails'
            ).execute()

            results = []
            for item in video_response.get('items', []):
                results.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'duration_seconds': self.parse_duration(item['contentDetails']['duration']),
                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                })
            return results

        except HttpError as e:
            error_msg = f"Error searching for videos: {str(e)}"
            if "quotaExceeded" in str(e):
                error_msg += " (API quota may be exhausted)"
            return [{"error": error_msg}]

    @retry(3, 1.0)
    def _get_channel_info(self, channel_id: str) -> Dict:
        try:
            response = self.service.channels().list(
                id=channel_id,
                part='snippet,statistics,contentDetails'
            ).execute()

            if not response.get('items'):
                return {"error": "Channel not found"}

            channel_info = response['items'][0]
            playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']

            video_list = []
            next_page_token = None
            for _ in range(self.max_results):
                playlist_items = self.service.playlistItems().list(
                    playlistId=playlist_id,
                    part='snippet,contentDetails',
                    maxResults=self.max_results,
                    pageToken=next_page_token
                ).execute()

                for item in playlist_items.get('items', []):
                    video_list.append({
                        'id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'published_at': item['snippet']['publishedAt']
                    })

                next_page_token = playlist_items.get('nextPageToken')
                if not next_page_token:
                    break

            return {
                'name': channel_info['snippet']['title'],
                'description': channel_info['snippet'].get('description', ''),
                'subscriber_count': int(channel_info['statistics'].get('subscriberCount', 0)),
                'total_view_count': int(channel_info['statistics'].get('viewCount', 0)),
                'total_video_count': int(channel_info['statistics'].get('videoCount', 0)),
                'latest_video_list': video_list
            }

        except HttpError as e:
            error_msg = f"Error analyzing channel: {str(e)}"
            if "quotaExceeded" in str(e):
                error_msg += " (API quota may be exhausted)"
            return {"error": error_msg}

    @retry(3, 1.0)
    def _get_trending_videos(self, region_code: Optional[str] = None) -> List[Dict]:
        try:
            request_param = {
                'part': 'snippet,statistics,contentDetails',
                'chart': 'mostPopular',
                'maxResults': self.max_results
            }
            if region_code:
                request_param['regionCode'] = region_code

            response = self.service.videos().list(**request_param).execute()

            results = []
            for item in response.get('items', []):
                view_count = int(item['statistics'].get('viewCount', 0))
                results.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': view_count,
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'duration_seconds': self.parse_duration(item['contentDetails']['duration']),
                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                })
            return results

        except HttpError as e:
            error_msg = f"Error getting trending videos: {str(e)}"
            if "quotaExceeded" in str(e):
                error_msg += " (API quota may be exhausted)"
            return [{"error": error_msg}]

    def execute(self,
            mode: str,
            input: Optional[str] = None
        ) -> List[Dict] | Dict:
        if self.service is None:
            self._initialize_service()

        if mode == Mode.VIDEO_SEARCH.value:
            if input is None:
                raise ValueError("Query string is required for video search mode.")
            return self._search_videos(input)
        elif mode == Mode.CHANNEL_INFO.value:
            if input is None:
                raise ValueError("Channel ID is required for channel info mode.")
            return self._get_channel_info(input)
        elif mode == Mode.TRENDING_VIDEOS.value:
            return self._get_trending_videos(input)
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in Mode]}")