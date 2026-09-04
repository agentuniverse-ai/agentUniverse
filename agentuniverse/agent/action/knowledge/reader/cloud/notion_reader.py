# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: notion_reader.py
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class NotionReader(Reader):
    """Reader for Notion pages/databases via Notion API.

    Requires:
        pip install notion-client
    Environment:
        NOTION_TOKEN must be provided (or pass via ext_info)
    """

    def _load_data(self, page_or_db_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Load a Notion page or database as a list of documents.

        Args:
            page_or_db_id: The Notion page or database id to read.
            ext_info: Optional extra info that may carry the Notion token.

        Returns:
            A list with a single Document whose text is the concatenated page
            or database content and whose metadata records the source and id.

        Raises:
            ValueError: If no page or database id is given.
            EnvironmentError: If no NOTION_TOKEN is available.
            ImportError: If the notion-client package is not installed.
            RuntimeError: If the Notion id can be neither read as page nor database.
        """
        print(f"debugging: NotionReader start load id={page_or_db_id}")
        if not page_or_db_id:
            raise ValueError("NotionReader requires a Notion page or database id")

        token = None
        if ext_info:
            token = ext_info.get("NOTION_TOKEN") or ext_info.get("notion_token")
        if not token:
            import os
            token = os.environ.get("NOTION_TOKEN")
        if not token:
            raise EnvironmentError("NOTION_TOKEN is required for NotionReader")

        try:
            from notion_client import Client  # type: ignore
        except Exception:
            raise ImportError("Install notion-client: `pip install notion-client`")

        client = Client(auth=token)
        text_blocks: List[str] = []
        metadata: Dict = {"source": "notion", "id": page_or_db_id}

        # Try as page
        try:
            page = client.pages.retrieve(page_id=page_or_db_id)
            metadata["type"] = "page"
            text_blocks.extend(self._export_page(client, page_or_db_id))
        except Exception as e_page:
            print(f"debugging: NotionReader page retrieve failed: {e_page}")
            # Try as database
            try:
                metadata["type"] = "database"
                for row in client.databases.query(database_id=page_or_db_id).get("results", []):
                    row_id = row.get("id")
                    text_blocks.extend(self._export_page(client, row_id))
            except Exception as e_db:
                raise RuntimeError(f"Failed to read Notion id={page_or_db_id}: {e_db}")

        text = "\n\n".join([b for b in text_blocks if b and b.strip()])
        if ext_info:
            metadata.update(self._public_metadata(ext_info))
        return [Document(text=text, metadata=metadata)]

    @staticmethod
    def _public_metadata(ext_info: Dict) -> Dict:
        """Filter out sensitive auth entries from extra info metadata.

        Args:
            ext_info: The raw extra info mapping to filter.

        Returns:
            A new dict containing only entries whose keys are not considered
            sensitive (e.g. token/auth related).
        """
        sensitive_keys = {
            "NOTION_TOKEN",
            "notion_token",
            "token",
            "auth",
            "authorization",
        }
        return {key: value for key, value in ext_info.items() if key not in sensitive_keys}

    def _export_page(self, client, page_id: str) -> List[str]:
        """Export every text block of a Notion page.

        Args:
            client: The initialized Notion API client.
            page_id: The Notion page id whose blocks are read.

        Returns:
            The list of non-empty text pieces converted from the page blocks,
            following pagination until all children are collected.
        """
        blocks: List[str] = []
        cursor = None
        while True:
            children = client.blocks.children.list(block_id=page_id, start_cursor=cursor)
            for blk in children.get("results", []):
                txt = self._block_to_text(blk)
                if txt:
                    blocks.append(txt)
            if not children.get("has_more"):
                break
            cursor = children.get("next_cursor")
        return blocks

    def _block_to_text(self, block: Dict) -> str:
        """Convert a Notion block dict into plain text.

        Args:
            block: A raw Notion block object.

        Returns:
            The concatenated rich text for textual block types, ``[table omitted]``
            for tables, ``[image]`` for images, or an empty string otherwise.
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
        if t in ("paragraph", "heading_1", "heading_2", "heading_3", "quote", "callout", "bulleted_list_item", "numbered_list_item", "to_do", "toggle"):
            return rich_text_to_str(data.get("rich_text", []))
        if t == "code":
            return rich_text_to_str(data.get("rich_text", []))
        if t == "table":
            return "[table omitted]"
        if t == "image":
            return "[image]"
        return ""
