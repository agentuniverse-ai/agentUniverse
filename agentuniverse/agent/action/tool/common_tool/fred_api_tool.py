from typing import Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from pydantic import Field
from agentuniverse.base.annotation.retry import retry
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

class SearchMode(Enum):
    """搜索模式枚举类"""
    SEARCH = "search"   # 数据集搜索模式
    DETAIL = "detail"   # 序列数据获取模式

class FredApiTool(Tool):
    """Fred宏观经济数据工具类，支持数据集搜索和时间序列数据获取"""
    
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")
    
    def __init__(self, api_key: str = None):
        """初始化Fred客户端"""
        super().__init__()
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("FRED API key must be provided or set in FRED_API_KEY environment variable")
        try:
            from fredapi import Fred
            self.fred_client = Fred(api_key=self.api_key)
        except ImportError:
            raise ImportError("fredapi is required. Install with: pip install fredapi")

    def execute(self, tool_input: ToolInput):
        """执行工具逻辑"""
        mode = tool_input.get_data('mode')
        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        query = tool_input.get_data("input")
        processed_query = self._process_query(query)

        return (self.search_datasets(processed_query) if mode == SearchMode.SEARCH.value
                else self.get_series_data(processed_query))

    def _process_query(self, query: str) -> str:
        """处理查询字符串，限制最大长度"""
        if len(query) <= self.MAX_QUERY_LENGTH:
            return query

        words = query.split()
        processed_words = []
        current_length = 0
        for word in words:
            word_length = len(word) + 1 
            if current_length + word_length <= self.MAX_QUERY_LENGTH:
                processed_words.append(word)
                current_length += word_length
            else:
                break
        return ' '.join(processed_words)

    @retry(3, 1.0)
    def search_datasets(self, keyword: str) -> str:
        """搜索宏观经济数据集"""
        try:
            result = self.fred_client.search(keyword, limit=10, order_by='popularity')
            if result.empty:
                return f"No datasets found for keyword: {keyword}"
                
            # 格式化输出搜索结果
            output = [f"Found {len(result)} datasets for '{keyword}':"]
            for idx, row in result.iterrows():
                output.append(
                    f"\n[{idx+1}] {row['title']}\n"
                    f"ID: {row['id']}\n"
                    f"Frequency: {row['frequency']}\n"
                    f"Units: {row['units']}\n"
                    f"Description: {row['notes'][:200]}..."
                )
            return "\n" + "-"*80 + "\n".join(output)
            
        except Exception as e:
            return f"Error searching datasets: {str(e)}"

    @retry(3, 1.0)
    def get_series_data(self, series_id: str) -> str:
        """获取时间序列数据"""
        try:
            import pandas as pd
            data = self.fred_client.get_series(series_id, limit=5)
            
            if isinstance(data, pd.Series) and data.empty:
                return f"No data found for series ID: {series_id}"
                
            # 格式化输出时间序列数据
            output = [f"Latest data for {series_id}:"]
            if isinstance(data, pd.Series):
                for date, value in data.items():
                    output.append(f"{date.strftime('%Y-%m-%d')}: {value}")
            else:  # 处理非时间序列数据
                output.append(str(data))
                
            return "\n".join(output)
            
        except Exception as e:
            return f"Error fetching series data: {str(e)}"
