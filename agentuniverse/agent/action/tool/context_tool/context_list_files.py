#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_list_files.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextListFilesTool(BaseContextTool):
    """Context list files tool
    
    List all file names saved in the context
    """
    
    name: str = "context_list_files"
    description: str = "List all file names saved in the context"
    
    def execute(self, session_id: str) -> Dict[str, Any]:
        """Execute file list operation
        
        Args:
            session_id: Session ID
            
        Returns:
            All file names and operation result
        """
        try:
            session_dir = self._get_session_directory(session_id)
            
            if not os.path.exists(session_dir):
                return {
                    "all_files": "",
                    "message": "Session directory does not exist"
                }
            
            # Get all files in directory
            files = []
            for item in os.listdir(session_dir):
                item_path = os.path.join(session_dir, item)
                if os.path.isfile(item_path):
                    files.append(item)
            
            if not files:
                return {
                    "all_files": "",
                    "message": "No files in this session"
                }
            
            # Sort files by name
            files.sort()
            all_files_str = ', '.join(files)
            
            return {
                "all_files": all_files_str,
                "message": "File list obtained successfully"
            }
            
        except Exception as e:
            return {
                "all_files": "",
                "message": f"Failed to get file list: {str(e)}"
            }
