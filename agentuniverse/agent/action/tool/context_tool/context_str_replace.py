#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_str_replace.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextStrReplaceTool(BaseContextTool):
    """Context string replacement tool
    
    Perform exact string replacement in specified file
    """
    
    name: str = "context_str_replace"
    description: str = "Perform exact string replacement in specified file"
    
    def execute(self, 
                file_name: str,
                old_str: str,
                new_str: str,
                session_id: str) -> Dict[str, Any]:
        """Execute string replacement operation
        
        Args:
            file_name: File name
            old_str: String to find and replace
            new_str: Replacement string
            session_id: Session ID
            
        Returns:
            Modified content and operation result
        """
        try:
            file_path = self._get_file_path(session_id, file_name)
            
            if not os.path.exists(file_path):
                return {
                    "result": "",
                    "message": f"File does not exist: {file_name}"
                }
            
            # Read file content
            content = self._read_file_content(file_path)
            
            # Check if old string exists
            if old_str not in content:
                return {
                    "result": content,
                    "message": f"No matching string found: {old_str}"
                }
            
            # Execute replacement
            new_content = content.replace(old_str, new_str)
            
            # Write updated content
            self._write_file_content(file_path, new_content)
            
            return {
                "result": new_content,
                "message": "String replacement successful"
            }
            
        except Exception as e:
            return {
                "result": "",
                "message": f"String replacement failed: {str(e)}"
            }
