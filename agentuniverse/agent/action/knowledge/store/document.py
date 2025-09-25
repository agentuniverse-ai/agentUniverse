# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/19 19:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: document.py
import uuid
from typing import Dict, Any, Optional, List, Set

from langchain_core.documents.base import Document as LCDocument
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

    @model_validator(mode="before")
    def create_id(cls, values):
        text: str = values.get("text", "")
        if not values.get("id"):
            values["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, text))
        return values

    def as_langchain(self) -> LCDocument:
        """Convert to LangChain document format."""
        metadata = self.metadata or {}
        return LCDocument(page_content=self.text, metadata=metadata)

    @staticmethod
    def as_langchain_list(document_list) -> List[LCDocument]:
        """Convert agentUniverse(aU) document list to langchain document list"""
        langchain_document_list = []
        if document_list is None:
            return langchain_document_list
        for document in document_list:
            langchain_document_list.append(LCDocument(page_content=document.text, metadata=document.metadata))
        return langchain_document_list

    @staticmethod
    def from_langchain_list(lc_document_list: List[LCDocument]):
        """Convert langchain document list to agentUniverse(aU) document list"""
        document_list = []
        if lc_document_list is None:
            return document_list
        for lc_document in lc_document_list:
            document_list.append(Document(text=lc_document.page_content, metadata=lc_document.metadata))
        return document_list
