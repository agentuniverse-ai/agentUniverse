#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_append_to_file.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextAppendToFileTool(BaseContextTool):
    """Context append content tool
    
    Append content to the end of specified file, preserving existing content
    """
    
    name: str = "context_append_to_file"
    description: str = "Append content to the end of specified file, preserving existing content"
    
    def execute(self, 
                file_name: str,
                content: str,
                session_id: str) -> Dict[str, Any]:
        """Execute content append operation
        
        Args:
            file_name: Target file name
            content: Content to append
            session_id: Session ID
            
        Returns:
            Operation result
        """
        try:
            file_path = self._get_file_path(session_id, file_name)
            
            # If file doesn't exist, create new file
            if not os.path.exists(file_path):
                self._write_file_content(file_path, content)
                return {
                    "message": "File does not exist, created new file and wrote content"
                }
            
            # Read existing content
            existing_content = self._read_file_content(file_path)
            
            # Append new content
            if existing_content:
                new_content = existing_content + '\n' + content
            else:
                new_content = content
            
            # Write updated content
            self._write_file_content(file_path, new_content)
            
            return {
                "message": "Content appended successfully"
            }
            
        except Exception as e:
            return {
                "message": f"Content append failed: {str(e)}"
            }
