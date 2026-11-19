# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/23 16:23
# @Author  : SaladDay
# @FileName: epub_reader.py
from pathlib import Path
from typing import Union, List, Optional, Dict
import re

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class EpubReader(Reader):
    """
    EPUB (.epub) file reader.

    Used to read and parse EPUB format e-books, supports chapter extraction and metadata parsing.
    Chapters follow the spine reading order. Documents outside the spine are
    retained afterwards in manifest order; an empty spine uses manifest order.
    """

    def _load_data(self, file: Union[str, Path], ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse EPUB file.

        Args:
            file: EPUB file path or file object
            ext_info: Additional metadata information

        Returns:
            List[Document]: List of documents containing EPUB content

        Note:
            `ebooklib` is required to read EPUB files: `pip install EbookLib`
        """
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            raise ImportError(
                "EbookLib is required to read EPUB files: "
                "`pip install EbookLib`"
            ) from None

        if isinstance(file, str):
            file = Path(file)

        # Load the EPUB book
        book = epub.read_epub(str(file))
        document_list = []

        # Extract book metadata
        book_metadata = {
            "file_name": file.name,
            "title": book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown",
            "author": book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown",
            "language": book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else "Unknown",
            "publisher": book.get_metadata('DC', 'publisher')[0][0] if book.get_metadata('DC', 'publisher') else "Unknown"
        }

        chapter_count = 0
        
        # The manifest lists resources, not their reading order. Resolve the
        # spine first, retaining unlisted resources afterwards for compatibility.
        items = list(book.get_items())
        items_by_id = {item.get_id(): item for item in items}
        ordered_items = []
        seen_ids = set()
        for item_id, _linear in book.spine:
            if item_id in items_by_id and item_id not in seen_ids:
                ordered_items.append(items_by_id[item_id])
                seen_ids.add(item_id)
        ordered_items.extend(item for item in items if item.get_id() not in seen_ids)

        # Process each item in reading order.
        for item in ordered_items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                chapter_count += 1
                
                # Extract text content from HTML
                content = item.get_content().decode('utf-8', errors='ignore')
                text_content = self._extract_text_from_html(content)
                
                if text_content.strip():  # Only add non-empty chapters
                    metadata = book_metadata.copy()
                    metadata.update({
                        "chapter_id": item.get_id(),
                        "chapter_file": item.get_name(),
                        "chapter_number": chapter_count,
                        "word_count": len(text_content.split())
                    })
                    
                    if ext_info is not None:
                        metadata.update(ext_info)
                    
                    document_list.append(Document(text=text_content, metadata=metadata))

        return document_list

    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content.
        
        Args:
            html_content: HTML string content
            
        Returns:
            str: Extracted plain text
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            #if BeautifulSoup is not available
            return self._extract_text_with_regex(html_content)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def _extract_text_with_regex(self, html_content: str) -> str:
        """Fallback method to extract text using regex when BeautifulSoup is not available.
        
        Args:
            html_content: HTML string content
            
        Returns:
            str: Extracted plain text
        """
        text = re.sub(r'<[^>]+>', '', html_content)
    
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
    
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
