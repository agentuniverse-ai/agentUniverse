# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/9 18:08
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_context.py

"""
AgentContext：Agent 运行时的状态容器。

设计原则：
1. 纯数据容器 —— 构造函数无副作用，不依赖外部服务
2. 单一数据源 —— 消息通过结构化字段管理，统一由 messages property 组装
3. 工厂创建   —— 通过 create() 完成依赖外部服务的初始化
4. 复用已有模型 —— 使用项目中已定义的 Message / ToolCall / FunctionCall
"""
from typing import List, Dict, Any, Optional, Union

from pydantic import BaseModel, Field

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message, ToolCall
from agentuniverse.llm.llm import LLM
from agentuniverse.base.util.logging.logging_util import LOGGER

from .models import (
    ToolCallRound, AgentProfile, AgentContextConfig,
    ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT, ROLE_TOOL,
    _make_message,
)
from .message_builder import MessageBuilder
from .tool_utils import build_tools_schema, estimate_tokens, serialize_tool_response


class AgentContext(BaseModel):
    """
    Agent 运行时状态容器。

    使用方式：
        ctx = AgentContext.create(
            agent_id="analyst_agent",
            profile=profile_dict,
            input_dict={"instruction": "分析这只股票", "query": "AAPL"},
            tool_names=["stock_search", "calculator"],
            llm=my_llm,
        )

        # 获取完整消息列表提交给 LLM
        messages = ctx.messages          # List[Dict]
        messages_raw = ctx.message_list  # List[Message]
    """

    # ====== 不可变配置 ======
    config: AgentContextConfig

    # ====== 消息状态（Single Source of Truth）======
    system_message: Optional[Message] = None
    chat_history: List[Message] = Field(default_factory=list)
    few_shot_messages: List[Message] = Field(default_factory=list)
    user_message: Optional[Message] = None

    # 多轮 tool calling 的完整历史
    tool_call_rounds: List[ToolCallRound] = Field(default_factory=list)
    # 当前正在进行的 tool calling 轮次
    _pending_tool_round: Optional[ToolCallRound] = None

    # 最终 assistant 回复
    assistant_message: Optional[Message] = None

    # ====== 推理内容追踪 ======
    reasoning_history: List[str] = Field(default_factory=list)

    # ====== 运行时引用（不参与序列化）======
    llm: Optional[LLM] = None
    memory: Optional[Memory] = None
    memory_config: Optional[Dict[str, Any]] = None
    output_stream: Optional[Any] = None
    tool_output_stream: Optional[Any] = None
    tool_instances: Dict[str, Any] = Field(default_factory=dict)

    # 原始输入，保留备用
    agent_input: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    # ================================================================
    # 工厂方法
    # ================================================================

    @classmethod
    def create(
        cls,
        agent_id: str,
        profile: Union[Dict[str, Any], AgentProfile],
        input_dict: Dict[str, Any],
        tool_names: Optional[List[str]] = None,
        llm: Optional[LLM] = None,
        memory: Optional[Memory] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> "AgentContext":
        """
        工厂方法：构建一个完整初始化的 AgentContext。
        依赖外部服务的逻辑（ToolManager 查询、消息构建）集中在这里。
        """
        agent_profile = AgentProfile(**profile) if isinstance(profile, dict) else profile
        tool_names = tool_names or []

        # 构建不可变配置
        config_kwargs: Dict[str, Any] = dict(
            agent_id=agent_id,
            profile=agent_profile,
            tool_names=tool_names,
            tool_execute_config=agent_profile.tool_execute_config,
        )
        if session_id:
            config_kwargs["session_id"] = session_id

        if tool_names:
            config_kwargs["tools_schema"] = build_tools_schema(tool_names)

        config = AgentContextConfig(**config_kwargs)

        # 构建消息（通过 MessageBuilder，不在 __init__ 中）
        system_message = MessageBuilder.build_system_message(agent_profile, input_dict)
        chat_history = MessageBuilder.load_chat_history(input_dict)
        few_shot_messages = MessageBuilder.build_few_shot_messages(agent_profile, input_dict)
        user_message = MessageBuilder.build_user_message(agent_profile, input_dict)

        return cls(
            config=config,
            system_message=system_message,
            chat_history=chat_history,
            few_shot_messages=few_shot_messages,
            user_message=user_message,
            llm=llm,
            memory=memory,
            agent_input=input_dict,
            **kwargs,
        )

    # ================================================================
    # 消息组装
    # ================================================================

    @property
    def message_list(self) -> List[Message]:
        """
        组装完整的 Message 对象列表。
        顺序：system → history → few_shot → user → tool_rounds → pending → assistant
        """
        result: List[Message] = []

        if self.system_message:
            result.append(self.system_message)
        result.extend(self.chat_history)
        result.extend(self.few_shot_messages)
        if self.user_message:
            result.append(self.user_message)

        # 已完成的 tool calling 轮次
        for round_ in self.tool_call_rounds:
            result.append(round_.assistant_message)
            result.extend(round_.tool_responses)

        # 当前进行中的 tool calling 轮次
        if self._pending_tool_round:
            result.append(self._pending_tool_round.assistant_message)
            result.extend(self._pending_tool_round.tool_responses)

        if self.assistant_message:
            result.append(self.assistant_message)

        return result

    @property
    def messages(self) -> List[Dict[str, Any]]:
        """
        组装完整的 LLM 消息列表（Dict 格式），直接提交给 LLM。
        这是唯一的序列化出口。

        使用 Message.to_dict() 而非直接 model_dump，
        确保与项目已有的序列化逻辑一致。
        """
        return [msg.to_dict() for msg in self.message_list]

    # ================================================================
    # 便捷属性
    # ================================================================

    @property
    def agent_id(self) -> str:
        return self.config.agent_id

    @property
    def session_id(self) -> str:
        return self.config.session_id

    @property
    def profile(self) -> AgentProfile:
        return self.config.profile

    @property
    def tool_names(self) -> List[str]:
        return self.config.tool_names

    @property
    def tools_schema(self) -> List[Dict[str, Any]]:
        return self.config.tools_schema

    @property
    def tool_execute_config(self) -> Dict[str, Any]:
        return self.config.tool_execute_config

    # ================================================================
    # 用户消息
    # ================================================================

    def update_user_message(self, input_dict: Dict[str, Any]) -> None:
        """更新用户消息（用于重试或修正输入）"""
        self.user_message = MessageBuilder.build_user_message(self.profile, input_dict)

    # ================================================================
    # Tool Calling 状态管理
    # ================================================================

    def start_tool_round(
        self,
        content: str,
        tool_calls: List[Union[ToolCall, Dict[str, Any]]],
        reasoning_content: Optional[str] = None,
    ) -> None:
        """
        开始一轮新的 tool calling。

        Args:
            content: assistant 消息的文本内容
            tool_calls: ToolCall 对象列表或兼容的 dict 列表
            reasoning_content: 可选的推理内容
        """
        # 如果上一轮没 finish，自动 finish
        if self._pending_tool_round:
            self.finish_tool_round()

        # 规范化 tool_calls：dict → ToolCall 对象
        normalized_tool_calls = _normalize_tool_calls(tool_calls)

        assistant_msg = _make_message(
            type=ROLE_ASSISTANT,
            content=content or "",
            tool_calls=normalized_tool_calls or None,
            reasoning_content=reasoning_content or None,
        )

        if reasoning_content:
            self.reasoning_history.append(reasoning_content)

        self._pending_tool_round = ToolCallRound(assistant_message=assistant_msg)

    def add_tool_response(self, tool_call_id: str, response: Any) -> None:
        """向当前 tool calling 轮次添加一条工具响应"""
        if not self._pending_tool_round:
            LOGGER.warning("add_tool_response called without an active tool round. Creating one implicitly.")
            self._pending_tool_round = ToolCallRound(
                assistant_message=_make_message(type=ROLE_ASSISTANT, content=""),
            )

        content = serialize_tool_response(response)
        self._pending_tool_round.tool_responses.append(
            _make_message(type=ROLE_TOOL, tool_call_id=tool_call_id, content=content)
        )

    def add_tool_responses(self, tool_responses: List[Dict[str, Any]]) -> None:
        """批量添加工具响应"""
        for resp in tool_responses:
            self.add_tool_response(
                tool_call_id=resp.get("tool_call_id", ""),
                response=resp.get("tool_response", resp.get("content", "")),
            )

    def finish_tool_round(self) -> None:
        """完成当前 tool calling 轮次，归档到历史"""
        if self._pending_tool_round:
            self.tool_call_rounds.append(self._pending_tool_round)
            self._pending_tool_round = None

    @property
    def tool_call_count(self) -> int:
        """已完成的 tool calling 轮次数"""
        return len(self.tool_call_rounds)

    @property
    def all_tool_messages(self) -> List[Message]:
        """所有 tool 相关消息的扁平列表"""
        messages: List[Message] = []
        for round_ in self.tool_call_rounds:
            messages.append(round_.assistant_message)
            messages.extend(round_.tool_responses)
        if self._pending_tool_round:
            messages.append(self._pending_tool_round.assistant_message)
            messages.extend(self._pending_tool_round.tool_responses)
        return messages

    def estimate_tool_tokens(self) -> int:
        """估算所有 tool 消息的 token 数"""
        return estimate_tokens(self.all_tool_messages)

    # ================================================================
    # Assistant 消息
    # ================================================================

    def update_assistant_message(self, content: str, reasoning_content: Optional[str] = None) -> None:
        """设置最终 assistant 回复"""
        self.assistant_message = _make_message(type=ROLE_ASSISTANT, content=content or "")
        if reasoning_content:
            self.reasoning_history.append(reasoning_content)

    # ================================================================
    # 历史消息管理
    # ================================================================

    def add_chat_history(self, messages: List[Any]) -> None:
        """追加历史消息"""
        for msg in messages:
            if isinstance(msg, Message):
                self.chat_history.append(msg)
            elif isinstance(msg, dict):
                self.chat_history.append(Message.from_dict(msg))

    # ================================================================
    # 兼容旧接口（过渡期，后续逐步移除）
    # ================================================================

    def add_tool_call_message(self, content: str, tool_calls: List[Any],
                              reasoning_content=None, **kwargs) -> None:
        """[Deprecated] → start_tool_round()"""
        self.start_tool_round(content, tool_calls, reasoning_content)

    def add_tool_response_messages(self, tool_responses: List[Dict[str, Any]]) -> None:
        """[Deprecated] → add_tool_responses()"""
        self.add_tool_responses(tool_responses)

    def clear_tool_messages(self) -> None:
        """[Deprecated] Tool rounds 自动管理，无需手动清理"""
        if self._pending_tool_round:
            self.finish_tool_round()

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """[Deprecated] → ctx.tools_schema"""
        return self.tools_schema

    def calculate_tool_messages_tokens(self) -> int:
        """[Deprecated] → estimate_tool_tokens()"""
        return self.estimate_tool_tokens()


# ================================================================
# 内部工具函数
# ================================================================

def _normalize_tool_calls(
    tool_calls: List[Union[ToolCall, Dict[str, Any]]],
) -> List[ToolCall]:
    """
    将混合类型的 tool_calls 列表统一为 List[ToolCall]。
    兼容旧代码传入 dict 的场景。
    """
    result = []
    for tc in tool_calls:
        if isinstance(tc, ToolCall):
            result.append(tc)
        elif isinstance(tc, dict):
            # 兼容 OpenAI 格式的 dict: {"id": "...", "type": "function", "function": {...}}
            try:
                if "function" in tc:
                    func = tc["function"]
                    result.append(ToolCall.create(
                        id=tc.get("id", ""),
                        name=func.get("name", ""),
                        arguments=func.get("arguments", "{}"),
                    ))
                else:
                    # 简化格式：{"id": "...", "name": "...", "arguments": "..."}
                    result.append(ToolCall.create(
                        id=tc.get("id", ""),
                        name=tc.get("name", ""),
                        arguments=tc.get("arguments", "{}"),
                    ))
            except Exception as e:
                LOGGER.warning(f"Failed to parse tool_call dict: {tc}, error: {e}")
        else:
            LOGGER.warning(f"Unexpected tool_call type: {type(tc)}")
    return result