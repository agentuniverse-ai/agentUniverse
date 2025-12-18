#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_download_files.py

import os
from typing import Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextDownloadFilesTool(BaseContextTool):
    """Context file download tool
    
    If users need to view files, use the download tool and provide file URL to users
    """
    
    name: str = "context_download_files"
    description: str = "Download context files, provide file access paths"
    
    def execute(self, 
                file_name: str,
                session_id: str) -> Dict[str, Any]:
        """Execute file download operation
        
        Args:
            file_name: File name, multiple files separated by comma
            session_id: Session ID
            
        Returns:
            File URL list and operation result
        """
        try:
            file_names = [f.strip() for f in file_name.split(',') if f.strip()]
            
            if not file_names:
                return {
                    "file_list": [],
                    "message": "No valid file names provided"
                }
            
            file_list = []
            
            for file_name_item in file_names:
                file_path = self._get_file_path(session_id, file_name_item)
                
                if not os.path.exists(file_path):
                    file_list.append({
                        "file": file_name_item,
                        "fileUrl": "",
                        "message": "File does not exist"
                    })
                    continue
                
                # Get relative path as file URL
                relative_path = self._get_relative_path(session_id, file_name_item)
                
                file_list.append({
                    "file": file_name_item,
                    "fileUrl": relative_path,
                    "message": "Download path obtained successfully"
                })
            
            return {
                "file_list": file_list,
                "message": "File download paths obtained successfully"
            }
            
        except Exception as e:
            return {
                "file_list": [],
                "message": f"File download failed: {str(e)}"
            }
