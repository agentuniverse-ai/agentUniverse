#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/15 20:34
# @Author  : wangyapei
# @FileName: tavily_tool.py
# @Need install: pip install tavily-python

from typing import Any, Dict, Literal, Optional, List

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.logging.logging_util import LOGGER

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("`tavily-python` not installed. Please install using `pip install tavily-python`")


class TavilyTool(Tool):
    """Tavily搜索工具，用于通过Tavily API进行网络搜索和网页内容提取。
    
    该工具可以执行两种操作：
    1. 搜索：返回结构化的搜索结果
    2. 网页提取：从指定URL提取网页内容
    
    Args:
        api_key (Optional[str]): Tavily API密钥，如果不提供则从环境变量获取
        search_depth (Literal["basic", "advanced"]): 搜索深度，可选"basic"或"advanced"
        max_results (int): 返回的最大结果数
        include_answer (bool): 是否包含AI生成的摘要答案
        mode (Literal["search", "extract"]): 操作模式，可选"search"或"extract"
    """
    description: str = "使用Tavily API进行网络搜索和网页内容提取，获取实时在线信息"

    # 基本配置参数
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("TAVILY_API_KEY"), description="Tavily API密钥")
    search_depth: Literal["basic", "advanced"] = Field(default="basic", description="搜索深度")
    include_answer: bool = Field(default=False, description="是否包含AI生成的摘要答案")
    mode: Literal["search", "extract"] = Field(default="search", description="操作模式：search或extract")
    
    # 搜索模式可选参数
    topic: Optional[Literal["general", "news"]] = Field(default=None, description="搜索主题：general或news")
    days: Optional[int] = Field(default=None, description="当topic为news时，指定搜索的天数")
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(default=None, description="搜索时间范围")
    max_results: int = Field(default=5, description="返回的最大结果数")
    include_domains: Optional[List[str]] = Field(default=None, description="包含的域名列表")
    exclude_domains: Optional[List[str]] = Field(default=None, description="排除的域名列表")
    include_raw_content: bool = Field(default=False, description="是否包含原始内容")
    include_images: bool = Field(default=False, description="是否包含图片")
    include_image_descriptions: bool = Field(default=False, description="是否包含图片描述")
    
    # 提取模式可选参数
    extract_depth: Literal["basic", "advanced"] = Field(default="advanced", description="提取深度")

    def execute(self, tool_input: ToolInput):
        """执行Tavily工具。
        
        Args:
            tool_input (ToolInput): 包含查询/URL和可选配置参数的输入对象
        
        Returns:
            Dict: 包含搜索结果或提取内容的字典
        """
        # 检查API密钥
        if not self.api_key:
            return {"error": "未提供Tavily API密钥，请设置TAVILY_API_KEY环境变量或在调用时提供api_key参数"}
            
        # 更新可选配置（如果提供）
        possible_params = [
            "api_key", "search_depth", "include_answer", "mode",
            "topic", "days", "time_range", "max_results", "include_domains", "exclude_domains",
            "include_raw_content", "include_images", "include_image_descriptions", "extract_depth"
        ]
        
        for param in possible_params:
            if tool_input.get_data(param) is not None:
                setattr(self, param, tool_input.get_data(param))

        try:
            # 初始化Tavily客户端
            client = TavilyClient(api_key=self.api_key)
            
            # 根据操作模式执行不同的操作
            if self.mode == "extract":
                # 提取模式
                urls = tool_input.get_data("input")
                if not urls:
                    return {"error": "未提供要提取内容的URL"}
                
                # 如果提供的是单个URL字符串，转换为列表
                if isinstance(urls, str):
                    urls = [urls]
                
                # 提取参数
                extract_params = {
                    "urls": urls,
                    "include_images": self.include_images,
                    "extract_depth": self.extract_depth
                }
                
                # 执行提取
                result = client.extract(**extract_params)
                # LOGGER.info(f"Tavily提取结果: {result}")
                
                # 直接返回API响应
                return result
            else:
                # 搜索模式
                query = tool_input.get_data("input")
                if not query:
                    return {"error": "未提供搜索查询"}
                
                # 搜索参数
                search_params = {
                    "query": query,
                    "search_depth": self.search_depth
                }
                
                # 添加其他可选参数（如果有设置）
                for param_name, param_attr in {
                    "topic": self.topic,
                    "days": self.days,
                    "time_range": self.time_range,
                    "max_results": self.max_results,
                    "include_domains": self.include_domains,
                    "exclude_domains": self.exclude_domains,
                    "include_answer": self.include_answer,
                    "include_raw_content": self.include_raw_content,
                    "include_images": self.include_images,
                    "include_image_descriptions": self.include_image_descriptions
                }.items():
                    if param_attr is not None:
                        search_params[param_name] = param_attr
                
                # 执行标准搜索
                result = client.search(**search_params)
                # LOGGER.info(f"Tavily搜索结果: {result}")
                
                # 直接返回API响应
                return result
                
        except Exception as e:
            LOGGER.error(f"Tavily操作出错: {e}")
            return {"error": f"操作过程中出错: {str(e)}"}
