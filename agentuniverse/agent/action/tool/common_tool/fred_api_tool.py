from typing import Optional, Any, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
import os
from datetime import datetime
from functools import lru_cache
from pydantic import Field, BaseModel
from agentuniverse.base.annotation.retry import retry
from agentuniverse.agent.action.tool.tool import Tool, ToolInput

class SearchMode(Enum):
    """搜索模式枚举类"""
    SEARCH = "search"   # 数据集搜索模式
    DETAIL = "detail"   # 序列数据获取模式


class FredQueryParams(BaseModel):
    """Fred查询参数模型"""
    limit: int = Field(default=10, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_order: str = Field(default="desc", pattern="^(desc|asc)$")
    filter_variable: str = Field(default="frequency", pattern="^(frequency|units| seasonal_adjustment)$")
    filter_value: str = "Monthly"
    observation_start:str=Field(default=datetime.now().strftime("%Y-%m-%d"))
    observation_end:str=Field(default=datetime.now().strftime("%Y-%m-%d"))
    realtime_start: str = Field(default=datetime.now().strftime("%Y-%m-%d"))

class FredApiTool(Tool):
    """增强版Fred宏观经济数据工具类"""
    
    MAX_QUERY_LENGTH: int = Field(default=300, description="查询字符串最大长度")
    fred_client: Any = Field(default=None)  # Fred客户端实例
    CACHE_SIZE: int = Field(default=128, description="API结果缓存大小")
    
    def __init__(self, api_key: str = Field(default=None)):
        """初始化Fred客户端"""
        super().__init__()
        cur_api_key = api_key or os.getenv("FRED_API_KEY")
        if not cur_api_key:
            raise ValueError("FRED API key must be provided or set in FRED_API_KEY environment variable")
        try:
            from fredapi import Fred
            self.fred_client = Fred(api_key=cur_api_key)
            self._setup_caching()
        except ImportError:
            raise ImportError("fredapi is required. Install with: pip install fredapi")

    def _setup_caching(self):
        """设置缓存机制"""
        self._get_series_data = lru_cache(maxsize=self.CACHE_SIZE)(self._get_series_data)
        self._search_datasets = lru_cache(maxsize=self.CACHE_SIZE)(self._search_datasets)
        # self._get_category_data = lru_cache(maxsize=self.CACHE_SIZE)(self._get_category_data)

    def execute(self, tool_input: ToolInput):
        """执行工具逻辑"""
        mode = tool_input.get_data('mode')
        if mode not in [m.value for m in SearchMode]:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {[m.value for m in SearchMode]}")

        query = tool_input.get_data("input")
        processed_query = self._process_query(query)
        params = tool_input.get_data("params") or {}

        if mode == SearchMode.SEARCH.value:
            return self._search_datasets(processed_query, **params)
        elif mode == SearchMode.DETAIL.value:
            return self._get_series_data(processed_query, **params)

        return "Unsupported operation"

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
    def _search_datasets(self, keyword: str, **kwargs) -> str:
        """增强型数据集搜索，支持高级参数过滤"""
        try:
            from pandas import DataFrame
            params = FredQueryParams(**kwargs)
            # print(f"Searching datasets with keyword: {keyword}")
            result = self.fred_client.search(
                keyword,
                limit=params.limit,
                # offset=params.offset,
                order_by=params.filter_variable,
                sort_order=params.sort_order

                # filter_value=params.filter_value
            )
            
            if not isinstance(result, DataFrame) or result.empty:
                return f"No datasets found for keyword: {keyword}"
                
            return self._format_search_results(result, keyword)
            
        except Exception as e:
            return f"Error searching datasets: {str(e)}"

    @retry(3, 1.0)
    def _get_series_data(self, series_id: str, **kwargs) -> str:
        """获取时间序列数据，支持参数化时间范围"""
        try:
            import pandas as pd
            # start_date = kwargs.get('realtime_start')
            # end_date = kwargs.get('realtime_end')
            observation_start = kwargs.get('observation_start')
            observation_end = kwargs.get('observation_end')
            print('observation_start',observation_start)
            
            data = self.fred_client.get_series(
                series_id, 
                # limit=kwargs.get('limit', 5),
                # offset=kwargs.get('offset', 0),
                observation_start=observation_start,
                observation_end=observation_end
                # realtime_start=start_date,
                # realtime_end=end_date
            )
            # print('data',data)
            
            if isinstance(data, pd.Series) and data.empty:
                return f"No data found for series ID: {series_id}"
                
            return self._format_series_data(data, series_id)
            
        except Exception as e:
            return f"Error fetching series data: {str(e)}"



    @retry(3, 1.0)
    def _get_series_metadata(self, series_id: str) -> str:
        """获取序列的元数据信息"""
        try:
            metadata = self.fred_client.get_series_info(series_id)
            if not metadata:
                return f"No metadata found for series ID: {series_id}"
                
            return self._format_metadata(metadata, series_id)
            
        except Exception as e:
            return f"Error fetching metadata: {str(e)}"

    def _format_search_results(self, result, keyword: str) -> str:
        """格式化搜索结果"""
        output = [f"Found {len(result)} datasets for '{keyword}':"]
        # print("格式化搜索结果",result)
        for idx, row in result.iterrows():
            output.append(
                row.to_string()
            )
        return "\n" + "-"*80 + "\n".join(output)
        # return

    def _format_series_data(self, data, series_id: str) -> str:
        """格式化时间序列数据"""
        output = [f"Latest data for {series_id}:"]
        if hasattr(data, 'items'):
            for date, value in data.items():
                output.append(f"{date.strftime('%Y-%m-%d')}: {value}")
        else:
            output.append(str(data))
        return "\n".join(output)

    def _format_category_data(self, result, category_id: str) -> str:
        """格式化分类数据"""
        output = [f"Series in category {category_id}:"]
        for idx, series in enumerate(result['seriess'], 1):
            output.append(
                f"\n[{idx}] {series['title']}\n"
                f"ID: {series['id']}\n"
                f"Description: {series['notes'][:150]}..."
            )
        return "\n" + "-"*80 + "\n".join(output)

    def _format_metadata(self, metadata, series_id: str) -> str:
        """格式化元数据"""
        print("格式化元数据",metadata,series_id)
        return (
            f"Metadata for {series_id}:\n"
            f"Title: {metadata.get('title', 'N/A')}\n"
            f"Observation Start: {metadata.get('observation_start', 'N/A')}\n"
            f"Observation End: {metadata.get('observation_end', 'N/A')}\n"
            f"Frequency: {metadata.get('frequency', 'N/A')}\n"
            f"Units: {metadata.get('units', 'N/A')}\n"
            f"Seasonal Adjustment: {metadata.get('seasonal_adjustment', 'N/A')}\n"
            f"Description: {metadata.get('notes', 'N/A')[:200]}..."
        )

    def clear_cache(self):
        """清除缓存"""
        self.get_series_data.cache_clear()
        self.search_datasets.cache_clear()
        self.get_category_data.cache_clear()
