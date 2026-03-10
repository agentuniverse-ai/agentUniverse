# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/19 19:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: document.py
import uuid
from typing import Dict, Any, Optional, List, Set

from pydantic import BaseModel, Field, model_validator


class Document(BaseModel):
    """The basic class for the document.

    Attributes:
        id (str): Unique identifier for the document.
        text (Optional[str]): The content of the document.
        metadata (Dict[str, Any]): Metadata associated with the document.
        embedding (List[float]): Embedding data associated with the document
    """
    class Config:
        arbitrary_types_allowed = True

    id: str = None
    text: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    embedding: List[float] = Field(default_factory=list)
    keywords: Set[str] = Field(default_factory=set)

    @model_validator(mode='before')
    def create_id(cls, values):
        text: str = values.get('text', '')
        if not values.get('id'):
            values['id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, text))
        return values
