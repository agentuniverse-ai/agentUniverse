# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 11:01
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: planner_dto.py
from typing import Optional, List

from pydantic import BaseModel, Field


class PlannerDTO(BaseModel):
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="planner nickname", default="")
    members: Optional[list] = Field(description="planner members", default=[])
    workflow_id: Optional[str] = None
