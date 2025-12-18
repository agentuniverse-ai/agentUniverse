#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_create_file.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextCreateFileTool(BaseContextTool):
    """Context file creation tool
    
    Used to create or update files in the context. Requires filename and content.
    If the file name already exists, it will overwrite and update the existing content.
    """
    
    name: str = "context_create_file"
    description: str = "Create or update context file"
    
    def execute(self, 
                file_name: str,
                content: str,
                session_id: str) -> Dict[str, Any]:
        """Execute file creation/update operation
        
        Args:
            file_name: File name
            content: File content
            session_id: Session ID
            
        Returns:
            Operation result and file URL
        """
        try:
            file_path = self._get_file_path(session_id, file_name)
            
            # Check if file already exists
            file_exists = os.path.exists(file_path)
            
            # Write file content (overwrite if file exists)
            self._write_file_content(file_path, content)
            
            # Get relative path as file URL
            file_url = self._get_relative_path(session_id, file_name)
            
            if file_exists:
                message = "File already exists, content updated"
            else:
                message = "File created successfully"
            
            return {
                "message": message,
                "file_url": file_url
            }
            
        except Exception as e:
            return {
                "message": f"File creation/update failed: {str(e)}",
                "file_url": ""
            }
