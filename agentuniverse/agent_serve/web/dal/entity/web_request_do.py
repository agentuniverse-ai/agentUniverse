#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: web_request_do.py

import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WebRequestDO(BaseModel):
    """Web请求数据对象类"""

    id: Optional[int] = Field(description="ID", default=None)
    request_id: str = Field(description="Unique request id.")
    session_id: str = Field(description="Session id of the request.")
    query: str = Field(description="The query contents.")
    state: str = Field(description="State of the request.")
    result: dict = Field(description="Exec result.")
    steps: list = Field(description="Exec steps.")
    additional_args: dict = Field(description="Additional info.")
    gmt_create: Optional[datetime.datetime] = Field(
        description="Create time", default_factory=datetime.datetime.now)
    gmt_modified: Optional[datetime.datetime] = Field(
        description="Modified time", default_factory=datetime.datetime.now)