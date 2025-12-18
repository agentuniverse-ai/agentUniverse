#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_rename_file.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextRenameFileTool(BaseContextTool):
    """Context rename file tool
    
    Rename a file to a new name
    """
    
    name: str = "context_rename_file"
    description: str = "Rename a file to a new name"
    
    def execute(self, 
                old_file_name: str,
                new_file_name: str,
                session_id: str) -> Dict[str, Any]:
        """Execute file rename operation
        
        Args:
            old_file_name: Original file name
            new_file_name: New file name
            session_id: Session ID
            
        Returns:
            Operation result
        """
        try:
            old_file_path = self._get_file_path(session_id, old_file_name)
            new_file_path = self._get_file_path(session_id, new_file_name)
            
            if not os.path.exists(old_file_path):
                return {
                    "message": f"Original file does not exist: {old_file_name}"
                }
            
            if os.path.exists(new_file_path):
                return {
                    "message": f"Target file already exists: {new_file_name}"
                }
            
            # Execute rename
            os.rename(old_file_path, new_file_path)
            
            return {
                "message": "File renamed successfully"
            }
            
        except Exception as e:
            return {
                "message": f"File rename failed: {str(e)}"
            }
