# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import inspect
import re
# @Time    : 2024/3/13 14:29
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool.py
from abc import abstractmethod
import json
from typing import List, Optional, get_type_hints, Any

from pydantic import BaseModel, validator
from langchain.tools import Tool as LangchainTool

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.base.annotation.trace import trace_tool
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.util.common_util import parse_and_check_json_markdown


class InputValidator:
    """输入验证器"""
    
    # 最大输入长度
    MAX_INPUT_LENGTH = 10000
    
    # 危险的模式
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS脚本
        r'javascript:',                # JavaScript协议
        r'data:text/html',             # 数据URI
        r'vbscript:',                  # VBScript协议
        r'onload\s*=',                 # 事件处理器
        r'onerror\s*=',                # 事件处理器
        r'eval\s*\(',                  # eval函数
        r'exec\s*\(',                  # exec函数
        r'import\s+os',                # 系统导入
        r'__import__\s*\(',            # 动态导入
        r'subprocess\.',               # 子进程调用
        r'os\.system',                 # 系统调用
    ]
    
    @classmethod
    def validate_input(cls, key: str, value: Any) -> bool:
        """验证输入参数"""
        try:
            # 检查字符串长度
            if isinstance(value, str):
                if len(value) > cls.MAX_INPUT_LENGTH:
                    return False
                
                # 检查危险模式
                for pattern in cls.DANGEROUS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                        return False
                
                # 检查SQL注入模式
                sql_patterns = [
                    r'union\s+select',
                    r'drop\s+table',
                    r'delete\s+from',
                    r'insert\s+into',
                    r'update\s+set',
                    r'--',  # SQL注释
                    r'/\*.*?\*/',  # SQL注释
                ]
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return False
            
            # 检查列表长度
            elif isinstance(value, list):
                if len(value) > 1000:  # 限制列表大小
                    return False
                
                # 递归验证列表中的元素
                for item in value:
                    if not cls.validate_input(f"{key}_item", item):
                        return False
            
            # 检查字典大小
            elif isinstance(value, dict):
                if len(value) > 100:  # 限制字典大小
                    return False
                
                # 递归验证字典中的值
                for k, v in value.items():
                    if not cls.validate_input(f"{key}_{k}", v):
                        return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def sanitize_input(cls, value: Any) -> Any:
        """清理输入数据"""
        if isinstance(value, str):
            # 移除控制字符
            sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
            return sanitized.strip()
        return value


class ToolInput(BaseModel):
    """The basic class for tool input."""

    def __init__(self, params: dict, **kwargs):
        super().__init__(**kwargs)
        self.__origin_params = params
        for k, v in params.items():
            self.__dict__[k] = v

    def to_dict(self):
        return self.__origin_params

    def to_json_str(self):
        return json.dumps(self.__origin_params, ensure_ascii=False)

    def add_data(self, key, value):
        self.__origin_params[key] = value
        self.__dict__[key] = value

    def get_data(self, key, default=None):
        return self.__origin_params.get(key, default)


class Tool(ComponentBase):
    """
    The basic class for tool model.

    Attributes:
        name (str): The name of the tool.
        description (str): The description of the tool.
        tool_type (ToolTypeEnum): The type of the tool.
        input_keys (Optional[List]): The input keys of the tool, e.g. ['input1', 'input2']
    """

    name: str = ""
    description: Optional[str] = None
    tool_type: ToolTypeEnum = ToolTypeEnum.FUNC
    input_keys: Optional[List] = None
    tracing: Optional[bool] = None
    as_mcp_tool: Any = None

    # tool's arg model and schema in dict form
    args_model: Any = None
    args_model_schema: Optional[dict] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.TOOL, **kwargs)

    @trace_tool
    def run(self, **kwargs):
        """The callable method that runs the tool."""
        self.input_check(kwargs)
        if self.check_execute_signature_deprecated():
            return self.execute(ToolInput(kwargs))
        return self.execute(**kwargs)

    @trace_tool
    async def async_run(self, **kwargs):
        """The callable method that runs the tool."""
        self.input_check(kwargs)
        return await self.async_execute(**kwargs)

    def input_check(self, kwargs: dict) -> None:
        """Enhanced input parameter validation"""
        if self.input_keys:
            for key in self.input_keys:
                if key not in kwargs.keys():
                    raise ValueError(f'{self.get_instance_code()} - The input must include key: {key}.')
                
                # 验证输入参数
                value = kwargs[key]
                if not InputValidator.validate_input(key, value):
                    raise ValueError(f'{self.get_instance_code()} - Invalid input for key: {key}')
                
                # 清理输入数据
                kwargs[key] = InputValidator.sanitize_input(value)

    @trace_tool
    def langchain_run(self, *args, callbacks=None, **kwargs):
        """The callable method that runs the tool."""
        if self.check_execute_signature_deprecated():
            """Deprecated in future, use kwargs as tool input instead of ToolInput."""
            tool_input = ToolInput(kwargs)
            parse_result = self.parse_react_input(args[0])
            for key in self.input_keys:
                tool_input.add_data(key, parse_result[key])
            return self.execute(tool_input)
        else:
            try:
                parse_result = parse_and_check_json_markdown(args[0],
                                                            self.input_keys)
            except Exception as e:
                return str(e)
            return self.execute(**parse_result)

    @trace_tool
    async def async_langchain_run(self, *args, callbacks=None, **kwargs):
        try:
            parse_result = parse_and_check_json_markdown(args[0], self.input_keys)
        except Exception as e:
            return str(e)
        return await self.async_execute(**parse_result)

    def parse_react_input(self, input_str: str):
        """
            parse react string to you input
            you can define your own logic here by override this function
        """
        return {
            self.input_keys[0]: input_str
        }

    @abstractmethod
    def execute(self, **kwargs):
        raise NotImplementedError

    async def async_execute(self, **kwargs):
        """The callable method that runs the tool."""
        return await asyncio.to_thread(self.execute, **kwargs)

    def as_langchain(self) -> LangchainTool:
        """Convert the agentUniverse(aU) tool class to the langchain tool class."""
        return LangchainTool(name=self.name,
                             func=self.langchain_run,
                             description=self.description)

    async def async_as_langchain(self) -> LangchainTool:
        return LangchainTool(name=self.name,
                             func=self.run,
                             coroutine=self.async_langchain_run,
                             description=self.description)

    def get_instance_code(self) -> str:
        """Return the full name of the tool."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: ToolConfiger) -> 'Tool':
        """Initialize the LLM by the ComponentConfiger object.
        Args:
            component_configer(LLMConfiger): the ComponentConfiger object
        Returns:
            Tool: the Tool object
        """
        try:
            # First handle the main configuration values
            for key, value in component_configer.configer.value.items():
                if key != 'metadata' and key != 'meta_class':  # Skip metadata field
                    setattr(self, key, value)
        except Exception as e:
            print(f"Error during configuration initialization: {str(e)}")
        self.name = component_configer.name
        self.description = component_configer.description
        if component_configer.tool_type:
            self.tool_type = next((member for member in ToolTypeEnum if
                                   member.value == component_configer.tool_type))
        self.input_keys = component_configer.input_keys
        if hasattr(component_configer, "tracing"):
            self.tracing = component_configer.tracing
        return self

    def create_copy(self):
        copied = self.model_copy()
        if self.input_keys is not None:
            copied.input_keys = self.input_keys.copy()
        return copied

    def check_execute_signature_deprecated(self) -> bool:
        """Check if the tool use deprecated execute definition which use
        ToolInput as input args."""
        if not hasattr(self, 'execute'):
            return False

        execute_method = getattr(self, 'execute')
        if not callable(execute_method):
            return False

        try:
            sig = inspect.signature(execute_method)
            params = sig.parameters
            if len(params) != 1:
                return False
            first_param = list(params.values())[0]
            try:
                type_hints = get_type_hints(execute_method)
                param_name = first_param.name
                if param_name not in type_hints:
                    return False
                param_type = type_hints[param_name]
                if param_type is not ToolInput:
                    return False
            except Exception as e:
                return False
            return True
        except ValueError:
            return False
        except TypeError:
            return False
