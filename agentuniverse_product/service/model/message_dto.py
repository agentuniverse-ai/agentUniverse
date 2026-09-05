# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: message_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class MessageDTO(BaseModel):
    """DTO model describing a message.
    """
    id: int = Field(description="ID")
    session_id: str = Field(description="Session ID")
    content: Optional[str] = Field(description="message content", default="")
    gmt_created: Optional[str] = Field(description="message create time")
    gmt_modified: Optional[str] = Field(description="message update time")
