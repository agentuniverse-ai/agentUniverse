# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: query.py

from PIL.Image import Image
from typing import Optional, List, Set

from pydantic import BaseModel, Field


class Query(BaseModel):
    """The basic class for the knowledge query.

    Attributes:
        query_str (Optional[str]): Origin query str.
        query_text_bundles (Optional[List[str]]): The query string list.
        query_image_bundles (Optional[List[Image]]): The query image list.
        keywords: (Optional[Set[str]]): Keywords used to search with inverted index.
        embeddings (List[List[float]]): A list of embedded queries.
        ext_info (dict): extra information used in query.
    """

    class Config:
        arbitrary_types_allowed = True

    query_str: Optional[str] = None
    query_text_bundles: Optional[List[str]] = Field(default_factory=list)
    query_image_bundles: Optional[List[Image]] = Field(default_factory=list)
    keywords: Optional[Set[str]] = Field(default_factory=set)
    embeddings: List[List[float]] = Field(default_factory=list)
    ext_info: dict = {}

    similarity_top_k: Optional[int] = None
