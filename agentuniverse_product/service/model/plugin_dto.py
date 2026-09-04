# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/27 15:53
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: plugin_dto.py
from typing import Optional, List

from pydantic import BaseModel, Field

from agentuniverse_product.service.model.tool_dto import ToolDTO


class PluginDTO(BaseModel):
    """DTO (data transfer object) representing a plugin.

    Attributes:
        id (str): The unique plugin id.
        nickname (Optional[str]): The plugin nickname.
        avatar (Optional[str]): The plugin avatar path.
        description (Optional[str]): The plugin description.
        toolset (Optional[List[ToolDTO]]): The tools provided by the plugin.
        openapi_desc (Optional[str]): The plugin OpenAPI schema description.
    """
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="plugin nickname", default="")
    avatar: Optional[str] = Field(description="plugin avatar path", default="")
    description: Optional[str] = Field(description="plugin description", default="")
    toolset: Optional[List[ToolDTO]] = Field(description="plugin toolset", default=[])
    openapi_desc: Optional[str] = Field(description="plugin openapi schema", default="")
