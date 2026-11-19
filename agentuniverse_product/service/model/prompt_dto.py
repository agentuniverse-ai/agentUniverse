# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/26 10:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class PromptDTO(BaseModel):
    """DTO model describing a prompt.
    """
    introduction: Optional[str] = Field(description="prompt introduction", default="")
    target: Optional[str] = Field(description="prompt target", default="")
    instruction: Optional[str] = Field(description="prompt instruction", default="")
