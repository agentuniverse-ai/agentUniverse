# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @FileName: __init__.py
"""Unified cloud document readers package.

This package groups every cloud-document reader behind a single, consistent
interface. ``CloudDocReader`` exposes an automatic, domain-based routing entry
point so callers do not need to pick the concrete reader manually.
"""
from agentuniverse.agent.action.knowledge.reader.cloud.cloud_doc_reader import (
    CloudDocReader,
    URL_PATTERN_MAP,
)
from agentuniverse.agent.action.knowledge.reader.cloud.confluence_reader import ConfluenceReader
from agentuniverse.agent.action.knowledge.reader.cloud.feishu_reader import FeishuReader
from agentuniverse.agent.action.knowledge.reader.cloud.google_docs_reader import GoogleDocsReader
from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader import NotionReader
from agentuniverse.agent.action.knowledge.reader.cloud.yuque_reader import YuqueReader

__all__ = [
    "CloudDocReader",
    "ConfluenceReader",
    "FeishuReader",
    "GoogleDocsReader",
    "NotionReader",
    "YuqueReader",
    "URL_PATTERN_MAP",
]
