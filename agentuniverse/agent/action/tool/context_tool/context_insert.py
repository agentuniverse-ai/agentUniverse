#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/7 16:20
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: context_insert.py

import os
from typing import Optional, Dict, Any

from agentuniverse.agent.action.tool.context_tool.base_context_tool import BaseContextTool


class ContextInsertTool(BaseContextTool):
    """Context insertion tool
    
    Insert text content after specified line number in a file
    """
    
    name: str = "context_insert"
    description: str = "Insert text content after specified line number in a file"
    
    def execute(self, 
                file_name: str,
                insert_text: str,
                session_id: str,
                insert_line: Optional[str] = None) -> Dict[str, Any]:
        """Execute insertion operation
        
        Args:
            file_name: Target file name
            insert_text: Text to insert
            session_id: Session ID
            insert_line: Insert line number (optional)
            
        Returns:
            Operation result
        """
        try:
            file_path = self._get_file_path(session_id, file_name)
            
            # If file doesn't exist, create new file
            if not os.path.exists(file_path):
                self._write_file_content(file_path, insert_text)
                return {
                    "message": "File does not exist, created new file and inserted content",
                    "result": "success"
                }
            
            # Read existing content
            content = self._read_file_content(file_path)
            lines = content.split('\n')
            
            # Process insertion line number
            if insert_line is None:
                # Default insert after last line
                lines.append(insert_text)
            else:
                try:
                    line_num = int(insert_line)
                    if line_num < 0:
                        return {
                            "message": "Insert line number cannot be negative",
                            "result": "error"
                        }
                    
                    if line_num == 0:
                        # Insert at beginning of file
                        lines.insert(0, insert_text)
                    elif line_num >= len(lines):
                        # Line number out of range, insert at end
                        lines.append(insert_text)
                    else:
                        # Insert after specified line
                        lines.insert(line_num, insert_text)
                except ValueError:
                    return {
                        "message": "Insert line number must be a valid number",
                        "result": "error"
                    }
            
            # Write updated content
            new_content = '\n'.join(lines)
            self._write_file_content(file_path, new_content)
            
            return {
                "message": "Content inserted successfully",
                "result": "success"
            }
            
        except FileNotFoundError:
            return {
                "message": f"File does not exist: {file_name}",
                "result": "error"
            }
        except Exception as e:
            return {
                "message": f"Content insertion failed: {str(e)}",
                "result": "error"
            }
