# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class MessageDTO(BaseModel):
    """DTO (data transfer object) representing a chat message within a session.

    Attributes:
        id (int): The unique message id.
        session_id (str): The id of the session the message belongs to.
        content (Optional[str]): The message content.
        gmt_created (Optional[str]): The message create time.
        gmt_modified (Optional[str]): The message update time.
    """
    id: int = Field(description="ID")
    session_id: str = Field(description="Session ID")
    content: Optional[str] = Field(description="message content", default="")
    gmt_created: Optional[str] = Field(description="message create time")
    gmt_modified: Optional[str] = Field(description="message update time")
