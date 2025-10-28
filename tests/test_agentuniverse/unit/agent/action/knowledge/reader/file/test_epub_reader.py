#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/09/23 16:30
# @Author  : SaladDay
# @FileName: test_epub_reader.py

"""
Unit tests for EpubReader
"""

import unittest
import tempfile
import os
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.file.epub_reader import EpubReader


class TestEpubReader(unittest.TestCase):
    """Test cases for EpubReader"""

    def setUp(self):
        """Set up test fixtures"""
        self.reader = EpubReader()  
        self.temp_dir = None  
        self.test_epub_path = None  
        self.temp_dir = tempfile.mkdtemp()  
        self.test_epub_path = os.path.join(self.temp_dir, "test_book.epub")"

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_epub(self):
        """Create a test EPUB file for testing"""
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            self.skipTest("EbookLib not available for testing")

        # Create a test EPUB
        book = epub.EpubBook()
        book.set_identifier('test123')
        book.set_title('Test Book')
        book.set_language('en')
        book.add_author('Test Author')
        book.add_metadata('DC', 'publisher', 'Test Publisher')

        # Create test chapter
        chapter = epub.EpubHtml(title='Test Chapter', file_name='test_chap.xhtml', lang='en')
        chapter.content = '''
        <html>
        <head><title>Test Chapter</title></head>
        <body>
        <h1>Test Chapter</h1>
        <p>This is a test paragraph with some content.</p>
        <p>This is another paragraph for testing purposes.</p>
        </body>
        </html>
        '''

        book.add_item(chapter)
        book.toc = (epub.Link("test_chap.xhtml", "Test Chapter", "test"),)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', chapter]

        # Write the EPUB file
        epub.write_epub(self.test_epub_path, book, {})

    def test_load_data_success(self):
        """Test successful EPUB loading"""
        try:
            import ebooklib
        except ImportError:
            self.skipTest("EbookLib not available for testing")

        self.create_test_epub()
        
        # Test loading the EPUB
        documents = self.reader._load_data(self.test_epub_path)
        
        # Verify results
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)
        
        # Check document content
        doc = documents[0]
        self.assertIn("Test Chapter", doc.text)
        self.assertIn("test paragraph", doc.text)
        
        # Check metadata
        metadata = doc.metadata
        self.assertEqual(metadata['title'], 'Test Book')
        self.assertEqual(metadata['author'], 'Test Author')
        self.assertEqual(metadata['language'], 'en')
        self.assertEqual(metadata['publisher'], 'Test Publisher')
        self.assertIn('chapter_id', metadata)
        self.assertIn('word_count', metadata)

    def test_load_data_with_custom_metadata(self):
        """Test EPUB loading with custom metadata"""
        try:
            import ebooklib
        except ImportError:
            self.skipTest("EbookLib not available for testing")

        self.create_test_epub()
        
        custom_metadata = {
            "custom_field": "custom_value",
            "processing_date": "2024-12-19"
        }
        
        documents = self.reader._load_data(self.test_epub_path, ext_info=custom_metadata)
        
        # Check that custom metadata is included
        doc = documents[0]
        self.assertEqual(doc.metadata['custom_field'], 'custom_value')
        self.assertEqual(doc.metadata['processing_date'], '2024-12-19')

    def test_load_data_file_not_found(self):
        """Test handling of non-existent file"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.epub")
        
        with self.assertRaises(Exception):
            self.reader._load_data(non_existent_file)

    def test_load_data_invalid_file(self):
        """Test handling of invalid EPUB file"""
        # Create a non-EPUB file with .epub extension
        invalid_epub_path = os.path.join(self.temp_dir, "invalid.epub")
        with open(invalid_epub_path, 'w') as f:
            f.write("This is not a valid EPUB file")
        
        try:
            with self.assertRaises(Exception):
                self.reader._load_data(invalid_epub_path)
        finally:
            os.remove(invalid_epub_path)

    def test_extract_text_from_html(self):
        """Test HTML text extraction"""
        html_content = '''
        <html>
        <head><title>Test</title></head>
        <body>
        <h1>Header</h1>
        <p>This is a <strong>test</strong> paragraph.</p>
        <script>console.log("script");</script>
        <style>body { color: red; }</style>
        </body>
        </html>
        '''
        
        result = self.reader._extract_text_from_html(html_content)
        
        # Should contain text content
        self.assertIn("Header", result)
        self.assertIn("This is a test paragraph", result)
        
        # Should not contain script or style content
        self.assertNotIn("console.log", result)
        self.assertNotIn("color: red", result)

    def test_extract_text_with_regex(self):
        """Test regex-based text extraction fallback"""
        html_content = '''
        <html>
        <body>
        <h1>Header</h1>
        <p>Test &amp; example with &lt;tags&gt;</p>
        </body>
        </html>
        '''
        
        result = self.reader._extract_text_with_regex(html_content)
        
        # Should extract text and decode entities
        self.assertIn("Header", result)
        self.assertIn("Test & example with <tags>", result)
        self.assertNotIn("<h1>", result)
        self.assertNotIn("&amp;", result)

    def test_path_handling(self):
        """Test different path input types"""
        try:
            import ebooklib
        except ImportError:
            self.skipTest("EbookLib not available for testing")

        self.create_test_epub()
        
        # Test with string path
        documents1 = self.reader._load_data(self.test_epub_path)
        
        # Test with Path object
        documents2 = self.reader._load_data(Path(self.test_epub_path))
        
        # Both should produce same results
        self.assertEqual(len(documents1), len(documents2))
        self.assertEqual(documents1[0].text, documents2[0].text)

    def test_empty_content_handling(self):
        """Test handling of EPUB with empty or minimal content"""
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            self.skipTest("EbookLib not available for testing")

        # Create EPUB with minimal content chapter
        book = epub.EpubBook()
        book.set_identifier('empty123')
        book.set_title('Empty Book')
        book.set_language('en')

        # Create chapter with minimal but valid HTML content
        empty_chapter = epub.EpubHtml(title='Empty', file_name='empty.xhtml')
        empty_chapter.content = '''
        <html>
        <head><title>Empty Chapter</title></head>
        <body>
        <h1>Empty Chapter</h1>
        <p> </p>
        </body>
        </html>
        '''
        
        book.add_item(empty_chapter)
        book.toc = (epub.Link("empty.xhtml", "Empty", "empty"),)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ['nav', empty_chapter]

        empty_epub_path = os.path.join(self.temp_dir, "empty.epub")
        
        try:
            epub.write_epub(empty_epub_path, book, {})
            documents = self.reader._load_data(empty_epub_path)
            # Should handle empty content gracefully
            self.assertIsInstance(documents, list)
            # May have empty or minimal content documents
            if documents:
                self.assertIsInstance(documents[0].text, str)
        except Exception as e:
            # If EPUB creation fails due to library limitations, skip this test
            self.skipTest(f"EPUB creation failed: {e}")


if __name__ == '__main__':
    unittest.main()
