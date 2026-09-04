# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: session_do.py
import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionDO(BaseModel):
    """Data object for a session record.

    Attributes:
        id: Primary key of the session record.
        session_id: Unique session ID.
        agent_id: ID of the agent the session belongs to.
        ext_info: Extra session information.
        gmt_created: Record creation time.
        gmt_modified: Record last modification time.
    """
    id: Optional[int] = Field(description="ID", default=None)
    session_id: str = Field(description="Session id")
    agent_id: str = Field(description="Agent id.")
    ext_info: Optional[dict] = Field(description="Session ext info.", default={})
    gmt_created: Optional[datetime.datetime] = Field(
        description="Create time", default_factory=datetime.datetime.now)
    gmt_modified: Optional[datetime.datetime] = Field(
        description="Modified time", default_factory=datetime.datetime.now)
