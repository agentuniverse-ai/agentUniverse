# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: google_search_tool.py

import json
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from pydantic import Field


class GoogleSearchTool(Tool):
    """增强的Google搜索工具。

    使用Google Serper API实现Google搜索功能，支持多种搜索类型和参数配置。

    特性:
        - 支持普通搜索、图片搜索、新闻搜索等
        - 可配置返回结果数量
        - 支持地理位置和语言设置
        - 提供详细的搜索结果信息

    注意:
        需要在 https://serper.dev 注册免费账户获取API密钥（每月2500次免费查询）。
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))
    default_k: int = Field(default=10, description="默认返回结果数量")
    default_gl: str = Field(default="us", description="地理位置代码")
    default_hl: str = Field(default="en", description="语言代码")

    def execute(self, input: str, search_type: str = "search", k: int = None, 
                gl: str = None, hl: str = None, **kwargs) -> str:
        """
        执行Google搜索
        
        Args:
            input: 搜索查询词
            search_type: 搜索类型 ("search", "images", "news", "places")
            k: 返回结果数量
            gl: 地理位置代码
            hl: 语言代码
            **kwargs: 其他参数
            
        Returns:
            格式化的搜索结果字符串
        """
        if not self.serper_api_key:
            return self._get_mock_result(input)
            
        k = k or self.default_k
        gl = gl or self.default_gl
        hl = hl or self.default_hl
        
        try:
            search = GoogleSerperAPIWrapper(
                serper_api_key=self.serper_api_key, 
                k=k, 
                gl=gl, 
                hl=hl, 
                type=search_type
            )
            result = search.run(query=input)
            return self._format_search_result(result, input, search_type)
        except Exception as e:
            return f"搜索出错: {str(e)}"

    async def async_execute(self, input: str, search_type: str = "search", k: int = None,
                           gl: str = None, hl: str = None, **kwargs) -> str:
        """异步执行Google搜索"""
        if not self.serper_api_key:
            return self._get_mock_result(input)
            
        k = k or self.default_k
        gl = gl or self.default_gl
        hl = hl or self.default_hl
        
        try:
            search = GoogleSerperAPIWrapper(
                serper_api_key=self.serper_api_key, 
                k=k, 
                gl=gl, 
                hl=hl, 
                type=search_type
            )
            result = await search.arun(query=input)
            return self._format_search_result(result, input, search_type)
        except Exception as e:
            return f"搜索出错: {str(e)}"

    def _format_search_result(self, result: str, query: str, search_type: str) -> str:
        """格式化搜索结果"""
        try:
            # 尝试解析JSON结果
            if isinstance(result, str) and result.startswith('['):
                data = json.loads(result)
                formatted = f"🔍 Google {search_type.title()} 搜索结果 (查询: {query}):\n\n"
                
                for i, item in enumerate(data[:5], 1):  # 只显示前5个结果
                    if isinstance(item, dict):
                        title = item.get('title', '无标题')
                        link = item.get('link', '')
                        snippet = item.get('snippet', '无描述')
                        formatted += f"{i}. **{title}**\n"
                        formatted += f"   🔗 {link}\n"
                        formatted += f"   📝 {snippet}\n\n"
                
                return formatted
            else:
                # 如果不是JSON格式，直接返回原始结果
                return f"🔍 Google {search_type.title()} 搜索结果 (查询: {query}):\n\n{result}"
        except Exception:
            return f"🔍 Google {search_type.title()} 搜索结果 (查询: {query}):\n\n{result}"

    def _get_mock_result(self, query: str) -> str:
        """返回模拟搜索结果（当API密钥不可用时）"""
        return f"""🔍 Google 搜索模拟结果 (查询: {query}):

⚠️ 注意: 未配置SERPER_API_KEY，显示模拟结果

1. **搜索结果示例 1**
   🔗 https://example.com/result1
   📝 这是关于"{query}"的示例搜索结果描述...

2. **搜索结果示例 2**
   🔗 https://example.com/result2
   📝 另一个关于"{query}"的相关信息...

请配置SERPER_API_KEY环境变量以获取真实搜索结果。
"""


class GoogleScholarSearchTool(Tool):
    """Google学术搜索工具。

    使用Google Serper API实现Google学术搜索功能，专门用于搜索学术论文和研究资料。

    特性:
        - 专门针对学术内容搜索
        - 支持按年份、作者、期刊等筛选
        - 提供论文引用信息
        - 支持多种学术搜索参数

    注意:
        需要在 https://serper.dev 注册免费账户获取API密钥。
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))
    default_k: int = Field(default=10, description="默认返回结果数量")

    def execute(self, input: str, year: str = None, author: str = None, 
                journal: str = None, k: int = None, **kwargs) -> str:
        """
        执行Google学术搜索
        
        Args:
            input: 搜索查询词
            year: 年份筛选 (如: "2020..2024")
            author: 作者筛选
            journal: 期刊筛选
            k: 返回结果数量
            **kwargs: 其他参数
            
        Returns:
            格式化的学术搜索结果字符串
        """
        if not self.serper_api_key:
            return self._get_mock_scholar_result(input)
            
        k = k or self.default_k
        
        # 构建学术搜索查询
        scholar_query = self._build_scholar_query(input, year, author, journal)
        
        try:
            search = GoogleSerperAPIWrapper(
                serper_api_key=self.serper_api_key, 
                k=k, 
                gl="us", 
                hl="en", 
                type="search"
            )
            result = search.run(query=scholar_query)
            return self._format_scholar_result(result, input, scholar_query)
        except Exception as e:
            return f"学术搜索出错: {str(e)}"

    async def async_execute(self, input: str, year: str = None, author: str = None,
                           journal: str = None, k: int = None, **kwargs) -> str:
        """异步执行Google学术搜索"""
        if not self.serper_api_key:
            return self._get_mock_scholar_result(input)
            
        k = k or self.default_k
        scholar_query = self._build_scholar_query(input, year, author, journal)
        
        try:
            search = GoogleSerperAPIWrapper(
                serper_api_key=self.serper_api_key, 
                k=k, 
                gl="us", 
                hl="en", 
                type="search"
            )
            result = await search.arun(query=scholar_query)
            return self._format_scholar_result(result, input, scholar_query)
        except Exception as e:
            return f"学术搜索出错: {str(e)}"

    def _build_scholar_query(self, query: str, year: str = None, author: str = None, 
                           journal: str = None) -> str:
        """构建学术搜索查询"""
        scholar_query = f"site:scholar.google.com {query}"
        
        if author:
            scholar_query += f" author:\"{author}\""
        if journal:
            scholar_query += f" journal:\"{journal}\""
        if year:
            scholar_query += f" {year}"
            
        return scholar_query

    def _format_scholar_result(self, result: str, original_query: str, scholar_query: str) -> str:
        """格式化学术搜索结果"""
        try:
            if isinstance(result, str) and result.startswith('['):
                data = json.loads(result)
                formatted = f"📚 Google学术搜索结果 (查询: {original_query}):\n\n"
                
                for i, item in enumerate(data[:5], 1):
                    if isinstance(item, dict):
                        title = item.get('title', '无标题')
                        link = item.get('link', '')
                        snippet = item.get('snippet', '无摘要')
                        
                        formatted += f"{i}. **{title}**\n"
                        formatted += f"   🔗 {link}\n"
                        formatted += f"   📖 {snippet}\n\n"
                
                return formatted
            else:
                return f"📚 Google学术搜索结果 (查询: {original_query}):\n\n{result}"
        except Exception:
            return f"📚 Google学术搜索结果 (查询: {original_query}):\n\n{result}"

    def _get_mock_scholar_result(self, query: str) -> str:
        """返回模拟学术搜索结果"""
        return f"""📚 Google学术搜索模拟结果 (查询: {query}):

⚠️ 注意: 未配置SERPER_API_KEY，显示模拟结果

1. **学术论文示例 1**
   🔗 https://scholar.google.com/example1
   📖 这是一篇关于"{query}"的学术论文摘要...

2. **学术论文示例 2**
   🔗 https://scholar.google.com/example2
   📖 另一篇相关的研究论文...

请配置SERPER_API_KEY环境变量以获取真实学术搜索结果。
"""
