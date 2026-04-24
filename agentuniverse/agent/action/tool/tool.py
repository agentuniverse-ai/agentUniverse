# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import asyncio
import json
from typing import List, Any
import inspect
from typing import get_origin, get_args, Union
# @Time    : 2024/3/13 14:29
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: tool.py
from typing import Optional

from pydantic import BaseModel

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.base.annotation.trace import trace_tool
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import \
    ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.tool_configer import \
    ToolConfiger

__all__ = ["Tool", "ToolInput", "ToolError", "ToolInputError", "ToolConfigError"]


class ToolError(Exception):
    """Base exception for Tool-related errors."""
    pass


class ToolInputError(ToolError, ValueError):
    """Raised when tool input validation fails."""
    pass


class ToolConfigError(ToolError):
    """Raised when tool configuration is invalid."""
    pass


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
    as_mcp_tool: Optional[Any] = None

    # tool's arg model and schema in dict form
    args_model: Any = None
    args_model_schema: Optional[dict] = None

    require_agent_context: bool = False

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.TOOL, **kwargs)

    @trace_tool
    def run(self, **kwargs):
        """The callable method that runs the tool."""
        self.input_check(kwargs)
        return self.execute(**kwargs)

    @trace_tool
    async def async_run(self, **kwargs):
        """The callable method that runs the tool."""
        self.input_check(kwargs)
        return await self.async_execute(**kwargs)

    def input_check(self, kwargs: dict) -> None:
        """Check whether the input parameters of the tool contain input keys of the tool"""
        if not self.input_keys:
            return
        missing = [k for k in self.input_keys if k not in kwargs]
        if missing:
            raise ToolInputError(
                f"{self.get_instance_code()} - Missing required input key(s): {missing}"
            )


    def parse_react_input(self, input_str: str):
        """
            parse react string to you input
            you can define your own logic here by override this function
        """
        return {
            self.input_keys[0]: input_str
        }

    def execute(self, **kwargs) -> Any:
        """Override this method to implement the tool's synchronous logic."""
        raise NotImplementedError(
            f"{self.get_instance_code()} - execute() is not implemented."
        )

    async def async_execute(self, **kwargs) -> Any:
        """Async implementation; defaults to running execute() in a thread pool.

        Override this method if your tool has native async support.

        .. note::
            The default implementation uses ``asyncio.to_thread``, so make sure
            ``execute()`` is **thread-safe** if you rely on the default behaviour.
        """
        return await asyncio.to_thread(self.execute, **kwargs)

    def get_instance_code(self) -> str:
        """Return a globally-unique identifier for this tool instance."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f"{appname}.{self.component_type.value.lower()}.{self.name}"

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

    def create_copy(self) -> "Tool":
        """Create a deep copy of this tool instance.

        Uses pydantic ``model_copy(deep=True)`` to ensure all mutable
        fields (input_keys, args_model_schema, etc.) are independently copied.
        """
        return self.model_copy(deep=True)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"tool_type={self.tool_type!r}, "
            f"input_keys={self.input_keys!r})>"
        )

    # ------------------------------------------------------------------ #
    #  OpenAI Function-Calling Schema 转换
    # ------------------------------------------------------------------ #

    def get_function_schema(self) -> dict:
        """将当前 Tool 转换为 OpenAI function-calling 格式的 tool 定义。

        解析优先级：
            1. 使用 ``args_model_schema`` （dict）——用户手动/YAML 显式声明的 JSON Schema
            2. 使用 ``args_model`` （Pydantic Model 类）自动生成 JSON Schema
            3. 反射子类 ``execute()`` （或 ``async_execute()``）方法签名，将类型注解转为 JSON Schema
            4. 兜底：用 ``input_keys`` 构造全 string 的 schema，或返回空 properties

        Returns:
            dict — 符合 OpenAI ``tools`` 参数格式::

                {
                    "type": "function",
                    "function": {
                        "name": "...",
                        "description": "...",
                        "parameters": { ... }
                    }
                }
        """
        parameters = self._resolve_parameters_schema()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description or "",
                "parameters": parameters,
            },
        }

        # -------------------- 内部：schema 解析调度 -------------------- #

    def _resolve_parameters_schema(self) -> dict:
        """按优先级依次尝试构建 parameters JSON Schema。"""

        # -------- 优先级 1a: 已有 dict 形式的 schema --------
        if self.args_model_schema:
            return self._normalize_schema(self.args_model_schema)

            # -------- 优先级 1b: Pydantic Model 类 --------
        if self.args_model is not None:
            try:
                # pydantic v2
                if hasattr(self.args_model, "model_json_schema"):
                    raw = self.args_model.model_json_schema()
                    # pydantic v1
                elif hasattr(self.args_model, "schema"):
                    raw = self.args_model.schema()
                else:
                    raw = None

                if raw is not None:
                    return self._normalize_schema(raw)
            except Exception:
                pass  # 降级到下一策略

        # -------- 优先级 2: 反射子类 execute()/async_execute() 签名 --------
        sig_schema = self._schema_from_execute_signature()
        if sig_schema is not None:
            return sig_schema

            # -------- 优先级 3: 兜底 --------
        return self._fallback_schema()

        # -------------------- 策略 2: 从 execute/async_execute 签名推导 -------------------- #

    def _schema_from_execute_signature(self) -> Optional[dict]:
        """反射 **子类** ``execute`` 或 ``async_execute`` 方法的类型注解，生成 JSON Schema。

        优先检查 ``execute()``；若无具名参数，再检查 ``async_execute()``。
        仅当子类对方法定义了具名参数（除 ``self`` 和 ``**kwargs``）时才生效。
        """
        return (self._schema_from_method_signature("execute")
                or self._schema_from_method_signature("async_execute"))

    def _schema_from_method_signature(self, method_name: str) -> Optional[dict]:
        """反射指定方法的类型注解，生成 JSON Schema。

        仅当方法定义了具名参数（除 ``self``、``*args``、``**kwargs``）时才生效。
        当 ``require_agent_context=True`` 时，``agent_context`` 参数也会被排除。
        """
        method = getattr(type(self), method_name, None)
        if method is None:
            return None

        try:
            sig = inspect.signature(method)
        except (ValueError, TypeError):
            return None

            # 过滤掉 self / *args / **kwargs
            # 当 require_agent_context=True 时，排除 agent_context 参数（不暴露给 LLM）
        meaningful_params = {
            name: p
            for name, p in sig.parameters.items()
            if name != "self"
               and p.kind
               not in (
                   inspect.Parameter.VAR_POSITIONAL,
                   inspect.Parameter.VAR_KEYWORD,
               )
               and not (self.require_agent_context and name == "agent_context")
        }

        if not meaningful_params:
            return None

        properties: dict = {}
        required: list = []

        for name, param in meaningful_params.items():
            prop_schema = self._annotation_to_property(param.annotation)

            # 无默认值 → required
            if param.default is inspect.Parameter.empty:
                required.append(name)
            else:
                # 把默认值记录到 schema 里（OpenAI 会参考）
                if param.default is not None:
                    prop_schema["default"] = param.default

            properties[name] = prop_schema

        schema: dict = {
            "type": "object",
            "properties": properties,
        }
        if required:
            schema["required"] = required

        return schema

        # -------------------- 策略 3: 兜底 -------------------- #

    def _fallback_schema(self) -> dict:
        """使用 ``input_keys`` 构造最简 schema；无 input_keys 则返回空。"""
        if self.input_keys:
            properties = {}
            for key in self.input_keys:
                properties[key] = {"type": "string", "description": ""}
            return {
                "type": "object",
                "properties": properties,
                "required": list(self.input_keys),
            }

            # 真正的兜底：允许任意 key-value
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

        # -------------------- 工具方法 -------------------- #

    @staticmethod
    def _normalize_schema(raw: dict) -> dict:
        """将 Pydantic / 用户自定义的 JSON Schema 裁剪为 OpenAI 可接受的格式。

        - 确保顶层包含 ``type: object`` 和 ``properties``。
        - 移除 OpenAI 不关心且可能报错的顶层字段（``title``, ``$defs``, ``definitions``）。
        - 保留 ``required`` / ``additionalProperties`` / ``description`` 等。
        """
        schema = dict(raw)  # shallow copy

        # 确保基本结构
        schema.setdefault("type", "object")
        schema.setdefault("properties", {})

        # 清理 Pydantic 自动生成、但 OpenAI 不需要的字段
        for key in ("title", "$defs", "definitions"):
            schema.pop(key, None)

            # 递归清理 properties 里每个字段的 title（可选，保持整洁）
        for prop_value in schema.get("properties", {}).values():
            if isinstance(prop_value, dict):
                prop_value.pop("title", None)

        return schema

    def _annotation_to_property(self, annotation) -> dict:
        """将单个 Python 类型注解转换为 JSON Schema property dict。

        支持:
            - 基本类型: str / int / float / bool / list / dict
            - Optional[X]  →  X 的类型
            - List[X]      →  {"type": "array", "items": ...}
            - Dict[K, V]   →  {"type": "object"}
            - Any / 无注解  →  {"type": "string"}  (安全兜底)
        """
        if annotation is inspect.Parameter.empty or annotation is Any:
            return {"type": "string"}

        return self._python_type_to_json_schema(annotation)

    def _python_type_to_json_schema(self, tp) -> dict:
        """递归地将 Python 类型映射为 JSON Schema 片段。"""

        _SIMPLE_MAP = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        # 1. 简单基本类型
        if tp in _SIMPLE_MAP:
            return {"type": _SIMPLE_MAP[tp]}

        origin = get_origin(tp)
        args = get_args(tp)

        # 2. Optional[X] = Union[X, None]
        if origin is Union:
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return self._python_type_to_json_schema(non_none[0])
                # 真正的 Union[A, B, ...] → anyOf
            return {
                "anyOf": [self._python_type_to_json_schema(a) for a in
                          non_none]
            }

            # 3. List[X]
        if origin is list:
            if args:
                return {
                    "type": "array",
                    "items": self._python_type_to_json_schema(args[0]),
                }
            return {"type": "array"}

            # 4. Dict[K, V]
        if origin is dict:
            result: dict = {"type": "object"}
            if args and len(args) == 2:
                result[
                    "additionalProperties"] = self._python_type_to_json_schema(
                    args[1])
            return result

            # 5. 尝试作为简单类型匹配（处理 typing 模块的别名）
        if hasattr(tp, "__origin__"):
            base = tp.__origin__
            if base in _SIMPLE_MAP:
                return {"type": _SIMPLE_MAP[base]}

                # 6. Pydantic model → 内联 schema
        if inspect.isclass(tp):
            if hasattr(tp, "model_json_schema"):
                return Tool._normalize_schema(tp.model_json_schema())
            if hasattr(tp, "schema"):
                return Tool._normalize_schema(tp.schema())

                # 7. 兜底
        return {"type": "string"}
