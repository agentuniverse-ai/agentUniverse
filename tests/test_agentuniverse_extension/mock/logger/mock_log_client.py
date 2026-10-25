# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 16:09
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mock_log_client.py

from aliyun.log.putlogsrequest import PutLogsRequest


class LogClient:
    """Mock class of aliyun.log.logclient.LogClient."""

    def __init__(self,
                 end_point: str,
                 access_key_id,
                 access_key_secret):
        """Initialize the __init__ instance.
        """
        self.endpoint = end_point
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def put_logs(self,request: PutLogsRequest):
        """Send the given log entries through the mocked client.
        """
        return True
