#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_read_files.py

import os
import re
from typing import Optional, Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextReadFilesTool(BaseContextTool):
    """Context file reading tool
    
    Read file content by specified name, support multiple files and line range reading
    """
    
    name: str = "context_read_files"
    description: str = "Read file content by specified name, support multiple files and line range reading"
    
    def execute(self, 
                file_name: str,
                session_id: str,
                line_range: Optional[str] = '',
                display_line_numbers: Optional[str] = "false") -> Dict[str, Any]:
        """Execute file reading operation
        
        Args:
            file_name: File name, multiple files separated by comma
            session_id: Session ID
            line_range: Read specified lines, example: [1, 10]
            display_line_numbers: Whether to display line numbers
            
        Returns:
            File content list and operation result
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
                        "content": "",
                        "message": "File does not exist"
                    })
                    continue
                
                # Read file content
                content = self._read_file_content(file_path)
                lines = content.split('\n')
                
                # Process line range
                if line_range:
                    try:
                        # Parse range format [start, end]
                        match = re.match(r'\[(\d+),\s*(\d+)\]', line_range)
                        if match:
                            start = int(match.group(1)) - 1  # Convert to 0-based index
                            end = int(match.group(2))
                            
                            if start < 0:
                                start = 0
                            if end > len(lines):
                                end = len(lines)
                            
                            if start >= end:
                                file_list.append({
                                    "file": file_name_item,
                                    "content": "",
                                    "message": "Invalid line range"
                                })
                                continue
                            
                            selected_lines = lines[start:end]
                        else:
                            file_list.append({
                                "file": file_name_item,
                                "content": "",
                                "message": "Invalid range format"
                            })
                            continue
                    except (ValueError, IndexError):
                        file_list.append({
                            "file": file_name_item,
                            "content": "",
                            "message": "Invalid line range"
                        })
                        continue
                else:
                    selected_lines = lines
                
                # Process line number display
                if display_line_numbers and display_line_numbers.lower() == "true":
                    numbered_lines = []
                    start_line = 1 if not line_range else (int(re.match(r'\[(\d+),\s*(\d+)\]', line_range).group(1)) if line_range else 1)
                    for i, line in enumerate(selected_lines):
                        numbered_lines.append(f"{start_line + i}: {line}")
                    file_content = '\n'.join(numbered_lines)
                else:
                    file_content = '\n'.join(selected_lines)
                
                file_list.append({
                    "file": file_name_item,
                    "content": file_content,
                    "message": "Read successfully"
                })
            
            return {
                "file_list": file_list,
                "message": "File reading successful"
            }
            
        except Exception as e:
            return {
                "file_list": [],
                "message": f"File reading failed: {str(e)}"
            }
