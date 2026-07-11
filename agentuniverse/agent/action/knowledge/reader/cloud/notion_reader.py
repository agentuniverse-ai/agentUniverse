# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: notion_reader.py
"""Reader for Notion pages and databases via the Notion api.

The optional ``notion-client`` package is imported lazily. Authentication uses
a Notion integration token provided through ``ext_info`` (``NOTION_TOKEN`` /
``notion_token``) or the ``NOTION_TOKEN`` environment variable.
"""
import os
from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.reader.reader_errors import (
    ReaderConfigError,
    ReaderDependencyError,
    ReaderLoadError,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.util.logging.logging_util import LOGGER


class NotionReader(Reader):
    """Reader for Notion pages/databases via Notion API.

    Requires:
        pip install notion-client
    Environment:
        NOTION_TOKEN must be provided (or pass via ext_info)
    """

    def _load_data(self, page_or_db_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a Notion page or database by id and return it as a Document.

        Args:
            page_or_db_id (str): The Notion page or database id.
            ext_info (Optional[Dict]): Optional runtime configuration, supports:
                - NOTION_TOKEN / notion_token (str): Notion auth token.

        Returns:
            List[Document]: Documents produced from the Notion resource.

        Raises:
            ReaderConfigError: If id or token is missing.
            ReaderDependencyError: If notion-client is not installed.
            ReaderLoadError: If the Notion resource cannot be read.
        """
        if not page_or_db_id:
            raise ReaderConfigError(
                "NotionReader requires a Notion page or database id.",
                reader_name=self.__class__.__name__,
            )
        LOGGER.debug(f"NotionReader start load id={page_or_db_id}")

        token = None
        if ext_info:
            token = ext_info.get("NOTION_TOKEN") or ext_info.get("notion_token")
        if not token:
            token = os.environ.get("NOTION_TOKEN")
        if not token:
            raise ReaderConfigError(
                "NOTION_TOKEN is required for NotionReader (pass via ext_info or env).",
                reader_name=self.__class__.__name__,
            )

        try:
            from notion_client import Client  # type: ignore
        except ImportError as e:
            raise ReaderDependencyError(
                "Install notion-client to use NotionReader: `pip install notion-client`",
                reader_name=self.__class__.__name__,
            ) from e

        client = Client(auth=token)
        text_blocks: List[str] = []
        metadata: Dict = {"source": "notion", "id": page_or_db_id}

        # Try as page first, then fall back to database
        try:
            client.pages.retrieve(page_id=page_or_db_id)
            metadata["type"] = "page"
            text_blocks.extend(self._export_page(client, page_or_db_id))
        except Exception as e_page:
            LOGGER.debug(f"NotionReader page retrieve failed, trying as database: {e_page}")
            try:
                metadata["type"] = "database"
                for row in client.databases.query(database_id=page_or_db_id).get("results", []):
                    row_id = row.get("id")
                    text_blocks.extend(self._export_page(client, row_id))
            except Exception as e_db:
                raise ReaderLoadError(
                    f"Failed to read Notion id={page_or_db_id}: {e_db}",
                    reader_name=self.__class__.__name__,
                ) from e_db

        text = "\n\n".join([b for b in text_blocks if b and b.strip()])
        if ext_info:
            metadata.update(ext_info)
        return [Document(text=text, metadata=metadata)]

    def _export_page(self, client, page_id: str) -> List[str]:
        """Export all text blocks of a Notion page.

        Args:
            client: The authenticated Notion client.
            page_id (str): The Notion page id.

        Returns:
            List[str]: Extracted text blocks.

        Raises:
            ReaderLoadError: If the blocks cannot be listed.
        """
        blocks: List[str] = []
        cursor = None
        try:
            while True:
                children = client.blocks.children.list(block_id=page_id, start_cursor=cursor)
                for blk in children.get("results", []):
                    txt = self._block_to_text(blk)
                    if txt:
                        blocks.append(txt)
                if not children.get("has_more"):
                    break
                cursor = children.get("next_cursor")
        except Exception as e:
            raise ReaderLoadError(
                f"Failed to list Notion blocks for page {page_id}: {e}",
                reader_name=self.__class__.__name__,
            ) from e
        return blocks

    def _block_to_text(self, block: Dict) -> str:
        """Convert a Notion block dict to plain text.

        Args:
            block (Dict): A Notion block object.

        Returns:
            str: Extracted plain text for the block (empty when unsupported).
        """
        t = block.get("type")
        data = block.get(t, {}) if t else {}

        def rich_text_to_str(items: List[Dict]) -> str:
            parts: List[str] = []
            for it in items or []:
                plain = it.get("plain_text") or ""
                if plain:
                    parts.append(plain)
            return "".join(parts)

        if t in ("paragraph", "heading_1", "heading_2", "heading_3", "quote",
                 "callout", "bulleted_list_item", "numbered_list_item", "to_do", "toggle"):
            return rich_text_to_str(data.get("rich_text", []))
        if t == "code":
            return rich_text_to_str(data.get("rich_text", []))
        if t == "table":
            return "[table omitted]"
        if t == "image":
            return "[image]"
        return ""
