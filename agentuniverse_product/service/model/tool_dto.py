# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:17
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool_dto.py
from typing import Optional, List

from pydantic import BaseModel, Field


class ToolDTO(BaseModel):
    """Data transfer object for a tool.

    Attributes:
        id: Tool ID.
        nickname: Tool nickname.
        avatar: Tool avatar path.
        description: Tool description.
        parameters: Tool parameter names.
        openapi_schema: OpenAPI schema for the tool.
    """
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="tool nickname", default="")
    avatar: Optional[str] = Field(description="tool avatar path", default="")
    description: Optional[str] = Field(description="tool description", default="")
    parameters: Optional[List[str]] = Field(description="tool parameters", default=[])
    openapi_schema: Optional[dict] = Field(description="openapi schema for tool", default={})
