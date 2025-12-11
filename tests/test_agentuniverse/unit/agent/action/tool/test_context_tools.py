#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_context_tools.py

import os
import tempfile
import unittest
from agentuniverse.agent.action.tool.context_tool.context_insert import ContextInsertTool
from agentuniverse.agent.action.tool.context_tool.context_read_files import ContextReadFilesTool
from agentuniverse.agent.action.tool.context_tool.context_str_replace import ContextStrReplaceTool
from agentuniverse.agent.action.tool.context_tool.context_append_to_file import ContextAppendToFileTool
from agentuniverse.agent.action.tool.context_tool.context_download_files import ContextDownloadFilesTool
from agentuniverse.agent.action.tool.context_tool.context_list_files import ContextListFilesTool
from agentuniverse.agent.action.tool.context_tool.context_rename_file import ContextRenameFileTool
from agentuniverse.agent.action.tool.context_tool.context_create_file import ContextCreateFileTool


class TestContextTools(unittest.TestCase):
    """Context tools test class"""
    
    def setUp(self):
        """Test setup"""
        # Create temporary directory as context root path
        self.temp_dir = tempfile.mkdtemp()
        
        # Set environment variable
        os.environ['CONTEXT_FILE_ROOTPATH'] = self.temp_dir
        
        # Initialize tool instances
        self.session_id = "test_session"
        
        self.insert_tool = ContextInsertTool()
        self.read_tool = ContextReadFilesTool()
        self.replace_tool = ContextStrReplaceTool()
        self.append_tool = ContextAppendToFileTool()
        self.download_tool = ContextDownloadFilesTool()
        self.list_tool = ContextListFilesTool()
        self.rename_tool = ContextRenameFileTool()
        self.create_tool = ContextCreateFileTool()
    
    def tearDown(self):
        """Test cleanup"""
        # Delete temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_context_create_file(self):
        """Test create file tool"""
        result = self.create_tool.execute(
            file_name="test_file",
            content="Hello, World!",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File created successfully")
        self.assertIn("session_test_session/test_file.md", result["file_url"])
    
    def test_context_read_files(self):
        """Test read files tool"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Line 1\nLine 2\nLine 3",
            session_id=self.session_id
        )
        
        # Test reading file
        result = self.read_tool.execute(
            file_name="test_file",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File reading successful")
        self.assertEqual(len(result["file_list"]), 1)
        self.assertEqual(result["file_list"][0]["file"], "test_file")
        self.assertIn("Line 1", result["file_list"][0]["content"])
    
    def test_context_insert(self):
        """Test insert content tool"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Line 1\nLine 3",
            session_id=self.session_id
        )
        
        # Insert content after line 1
        result = self.insert_tool.execute(
            file_name="test_file",
            insert_text="Line 2",
            insert_line="1",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "Content inserted successfully")
        self.assertEqual(result["result"], "success")
    
    def test_context_str_replace(self):
        """Test string replacement tool"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Hello World!",
            session_id=self.session_id
        )
        
        # Replace string
        result = self.replace_tool.execute(
            file_name="test_file",
            old_str="Hello",
            new_str="Hi",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "String replacement successful")
        self.assertIn("Hi World!", result["result"])
    
    def test_context_append_to_file(self):
        """Test append content tool"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Original content",
            session_id=self.session_id
        )
        
        # Append content
        result = self.append_tool.execute(
            file_name="test_file",
            content="Appended content",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "Content appended successfully")
    
    def test_context_list_files(self):
        """Test list files tool"""
        # Create some files
        self.create_tool.execute(
            file_name="file1",
            content="Content 1",
            session_id=self.session_id
        )
        self.create_tool.execute(
            file_name="file2",
            content="Content 2",
            session_id=self.session_id
        )
        
        # List files
        result = self.list_tool.execute(session_id=self.session_id)
        
        self.assertEqual(result["message"], "File list obtained successfully")
        self.assertIn("file1.md", result["all_files"])
        self.assertIn("file2.md", result["all_files"])
    
    def test_context_rename_file(self):
        """Test rename file tool"""
        # Create file first
        self.create_tool.execute(
            file_name="old_file",
            content="Content",
            session_id=self.session_id
        )
        
        # Rename file
        result = self.rename_tool.execute(
            old_file_name="old_file",
            new_file_name="new_file",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File renamed successfully")
    
    def test_context_download_files(self):
        """Test download files tool"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Download content",
            session_id=self.session_id
        )
        
        # Get download path
        result = self.download_tool.execute(
            file_name="test_file",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File download paths obtained successfully")
        self.assertEqual(len(result["file_list"]), 1)
        self.assertEqual(result["file_list"][0]["file"], "test_file")
        self.assertIn("session_test_session/test_file.md", result["file_list"][0]["fileUrl"])
    
    def test_context_read_files_with_range(self):
        """Test read files tool line range functionality"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
            session_id=self.session_id
        )
        
        # Test reading specified line range
        result = self.read_tool.execute(
            file_name="test_file",
            session_id=self.session_id,
            line_range="[2, 4]"
        )
        
        self.assertEqual(result["message"], "File reading successful")
        self.assertIn("Line 2", result["file_list"][0]["content"])
        self.assertIn("Line 3", result["file_list"][0]["content"])
        self.assertNotIn("Line 1", result["file_list"][0]["content"])
        self.assertNotIn("Line 5", result["file_list"][0]["content"])
    
    def test_context_insert_at_beginning(self):
        """Test insert content at beginning of file"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Original content",
            session_id=self.session_id
        )
        
        # Insert content at beginning of file
        result = self.insert_tool.execute(
            file_name="test_file",
            insert_text="New content at beginning",
            insert_line="0",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "Content inserted successfully")
        self.assertEqual(result["result"], "success")
    
    def test_context_insert_at_end(self):
        """Test insert content at end of file"""
        # Create file first
        self.create_tool.execute(
            file_name="test_file",
            content="Original content",
            session_id=self.session_id
        )
        
        # Insert content at end of file (no insert_line specified)
        result = self.insert_tool.execute(
            file_name="test_file",
            insert_text="New content at end",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "Content inserted successfully")
        self.assertEqual(result["result"], "success")
    
    def test_context_read_files_multiple_files(self):
        """Test reading multiple files"""
        # Create multiple files
        self.create_tool.execute(
            file_name="file1",
            content="Content 1",
            session_id=self.session_id
        )
        self.create_tool.execute(
            file_name="file2", 
            content="Content 2",
            session_id=self.session_id
        )
        
        # Test reading multiple files
        result = self.read_tool.execute(
            file_name="file1,file2",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File reading successful")
        self.assertEqual(len(result["file_list"]), 2)
        self.assertEqual(result["file_list"][0]["file"], "file1")
        self.assertEqual(result["file_list"][1]["file"], "file2")
    
    def test_context_download_files_multiple_files(self):
        """Test downloading multiple files"""
        # Create multiple files
        self.create_tool.execute(
            file_name="file1",
            content="Content 1",
            session_id=self.session_id
        )
        self.create_tool.execute(
            file_name="file2",
            content="Content 2",
            session_id=self.session_id
        )
        
        # Test downloading multiple files
        result = self.download_tool.execute(
            file_name="file1,file2",
            session_id=self.session_id
        )
        
        self.assertEqual(result["message"], "File download paths obtained successfully")
        self.assertEqual(len(result["file_list"]), 2)
        self.assertEqual(result["file_list"][0]["file"], "file1")
        self.assertEqual(result["file_list"][1]["file"], "file2")
