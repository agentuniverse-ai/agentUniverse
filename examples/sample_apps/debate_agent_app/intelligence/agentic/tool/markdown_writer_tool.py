#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/01 16:00
# @Author  : zhouxiaoji
# @Email   : zh_xiaoji@qq.com
# @FileName: markdown_writer_tool.py
import os
from typing import Optional
import datetime
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class MarkdownWriterTool(Tool):

    output_dir: Optional[str] = Field(default="./output")

    def execute(self, tool_input: ToolInput)->None:
        title: str = tool_input.get_data("title", "执行结果摘要")
        content: str = tool_input.get_data("content")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"debate_result_{title}_{today}.md"
        os.makedirs(self.output_dir, exist_ok=True)
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
