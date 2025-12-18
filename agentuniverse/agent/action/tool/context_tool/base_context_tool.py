#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: base_context_tool.py

import os
from abc import ABC

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class BaseContextTool(Tool, ABC):
    """Context tool base class
    
    Provides basic functionality for session_id directory management
    All context tools inherit from this class
    """
    
    context_file_rootpath: str = Field(
        default_factory=lambda: get_from_env("CONTEXT_FILE_ROOTPATH") if get_from_env("CONTEXT_FILE_ROOTPATH") else "/tmp/agentuniverse_context",
        description="Context file root path"
    )
    
    def _get_session_directory(self, session_id: str) -> str:
        """Get directory path for session_id
        
        Args:
            session_id: Session ID
            
        Returns:
            Session directory path
        """
        return os.path.join(self.context_file_rootpath, f"session_{session_id}")
    
    def _ensure_session_directory(self, session_id: str) -> str:
        """Ensure session_id directory exists
        
        Args:
            session_id: Session ID
            
        Returns:
            Session directory path
        """
        session_dir = self._get_session_directory(session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def _get_file_path(self, session_id: str, file_name: str) -> str:
        """Get full file path
        
        Args:
            session_id: Session ID
            file_name: File name
            
        Returns:
            Full file path
        """
        # If no extension, default to .md
        if '.' not in file_name:
            file_name = f"{file_name}.md"
        
        session_dir = self._ensure_session_directory(session_id)
        return os.path.join(session_dir, file_name)
    
    def _file_exists(self, session_id: str, file_name: str) -> bool:
        """Check if file exists
        
        Args:
            session_id: Session ID
            file_name: File name
            
        Returns:
            Whether file exists
        """
        file_path = self._get_file_path(session_id, file_name)
        return os.path.exists(file_path)
    
    def _read_file_content(self, file_path: str) -> str:
        """Read file content
        
        Args:
            file_path: File path
            
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File does not exist: {file_path}")
        except Exception as e:
            raise Exception(f"File reading failed: {str(e)}")
    
    def _write_file_content(self, file_path: str, content: str) -> None:
        """Write file content
        
        Args:
            file_path: File path
            content: Content to write
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"File writing failed: {str(e)}")
    
    def _get_relative_path(self, session_id: str, file_name: str) -> str:
        """Get file path relative to root path
        
        Args:
            session_id: Session ID
            file_name: File name
            
        Returns:
            Relative path
        """
        if '.' not in file_name:
            file_name = f"{file_name}.md"
        return f"session_{session_id}/{file_name}"
