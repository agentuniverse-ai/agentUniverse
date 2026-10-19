# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/9/29
# @FileName: notion_reader.py
from typing import List, Optional, Dict, ClassVar

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class NotionReader(Reader):
    """Reader for Notion pages/databases via Notion API.

    Requires:
        pip install notion-client
    Environment:
        NOTION_TOKEN must be provided (or pass via ext_info)
    """

    MAX_BLOCK_DEPTH: ClassVar[int] = 32
    MAX_BLOCKS: ClassVar[int] = 10000
    MAX_BLOCK_PAGES: ClassVar[int] = 1000

    def _load_data(self, page_or_db_id: str, ext_info: Optional[Dict] = None) -> List[Document]:
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
        sensitive_keys = {
            "NOTION_TOKEN",
            "notion_token",
            "token",
            "auth",
            "authorization",
        }
        return {key: value for key, value in ext_info.items() if key not in sensitive_keys}

    def _export_page(self, client, page_id: str) -> List[str]:
        """Export child blocks depth first, bounding nesting and API pagination.

        Limits raise ValueError rather than returning a truncated page.
        """
        blocks: List[str] = []
        block_count = 0

        def export_children(block_id: str, depth: int) -> None:
            nonlocal block_count
            if depth > self.MAX_BLOCK_DEPTH:
                raise ValueError("Notion block depth limit exceeded")
            cursor = None
            seen_cursors = set()
            for _ in range(self.MAX_BLOCK_PAGES):
                children = client.blocks.children.list(block_id=block_id, start_cursor=cursor)
                for blk in children.get("results", []):
                    block_count += 1
                    if block_count > self.MAX_BLOCKS:
                        raise ValueError("Notion block count limit exceeded")
                    txt = self._block_to_text(blk)
                    if txt:
                        blocks.append(txt)
                    if blk.get("has_children") and blk.get("id"):
                        export_children(blk["id"], depth + 1)
                if not children.get("has_more"):
                    return
                cursor = children.get("next_cursor")
                if not cursor or cursor in seen_cursors:
                    raise ValueError("Notion returned a missing or repeated pagination cursor")
                seen_cursors.add(cursor)
            raise ValueError("Notion block pagination limit exceeded")

        export_children(page_id, 0)
        return blocks

    def _block_to_text(self, block: Dict) -> str:
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
