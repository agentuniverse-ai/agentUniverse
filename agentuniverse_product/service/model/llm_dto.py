# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 23:27
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_dto.py
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class LlmDTO(BaseModel):
    """DTO (data transfer object) describing an LLM (large language model) configuration.

    Attributes:
        id (str): The unique LLM id.
        nickname (Optional[str]): The LLM nickname.
        temperature (Optional[float]): The LLM sampling temperature.
        model_name (Optional[List[str]]): The LLM model names.
    """
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="llm nickname", default="")
    temperature: Optional[float] = Field(description="llm temperature", default=None)
    model_name: Optional[List[str]] = Field(description="llm model name list", default=[])

    # pydantic protected_namespaces config
    model_config = ConfigDict(protected_namespaces=())
