# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 14:26
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: session_dto.py
from typing import Optional

from pydantic import BaseModel, Field

from agentuniverse_product.service.model.message_dto import MessageDTO


class SessionDTO(BaseModel):
    """DTO (data transfer object) representing an agent session.

    Attributes:
        id (str): The unique session id.
        agent_id (str): The id of the agent the session belongs to.
        messages (Optional[list[MessageDTO]]): The messages in the session.
        gmt_created (Optional[str]): The session create time.
        gmt_modified (Optional[str]): The session update time.
    """
    id: str = Field(description="ID")
    agent_id: str = Field(description="session agent id")
    messages: Optional[list[MessageDTO]] = Field(description="session messages", default=[])
    gmt_created: Optional[str] = Field(description="session create time")
    gmt_modified: Optional[str] = Field(description="session update time")
