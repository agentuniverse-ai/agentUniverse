# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 16:12
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: workflow_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowDTO(BaseModel):
    """DTO model describing a workflow.
    """
    id: Optional[str] = Field(description="ID", default=None)
    name: Optional[str] = Field(description="workflow name", default="")
    description: Optional[str] = Field(description="workflow description", default="")
    graph: Optional[dict] = Field(description="workflow graph config", default=None)
