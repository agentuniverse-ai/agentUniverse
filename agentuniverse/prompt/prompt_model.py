# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/12 19:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt_model.py
"""Agent Prompt Model module."""
from typing import ClassVar, Optional, Dict, List, Tuple

from pydantic import BaseModel, Field, model_validator

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message


class FewShotExample(BaseModel):
    """单条 few-shot 示例，包含用户输入和期望的助手输出。"""
    input: str
    output: str


DEFAULT_MESSAGE_TYPE_MAPPING: Dict[str, ChatMessageEnum] = {
    "introduction": ChatMessageEnum.SYSTEM,
    "target": ChatMessageEnum.SYSTEM,
    "few_shot_examples": ChatMessageEnum.HUMAN,
    "output_format": ChatMessageEnum.SYSTEM,
    "instruction": ChatMessageEnum.HUMAN,
}


DEFAULT_ASSEMBLE_ORDER: List[str] = [
    "introduction", "target", "few_shot_examples",
    "output_format", "instruction",
]


class AgentPromptModel(BaseModel):
    """Agent Prompt Model — prompt 内容的结构化表示。

    支持三种使用方式：
    1. 经典字段: introduction / target / few_shot_examples / output_format / instruction
    2. 自定义 sections: 通过 sections dict 添加任意段落
    3. 混合: 经典字段 + 自定义 sections 共存

    Attributes:
        introduction: 系统角色介绍（SYSTEM）。
        target: 任务目标描述（SYSTEM）。
        few_shot_examples: few-shot 示例列表，每条展开为一对 HUMAN+AI message。
        output_format: 输出格式要求（SYSTEM）。
        instruction: 用户指令模板（HUMAN）。
        sections: 额外的自定义段落，key 为段落名，value 为内容。
        message_type_mapping: section 名 -> ChatMessageEnum 的映射。
    """

    introduction: Optional[str] = None
    target: Optional[str] = None
    few_shot_examples: Optional[List[FewShotExample]] = None
    output_format: Optional[str] = None
    instruction: Optional[str] = None

    # 扩展段落：支持任意自定义 section
    sections: Dict[str, str] = Field(default_factory=dict)

    # message type 映射（显式字段，不再用下划线私有属性）
    message_type_mapping: Dict[str, ChatMessageEnum] = Field(
        default_factory=lambda: dict(DEFAULT_MESSAGE_TYPE_MAPPING)
    )

    # 所有经典 str 字段名（few_shot_examples 单独处理，因为类型不同）
    _NAMED_STR_FIELDS: ClassVar[Tuple[str, ...]] = ("introduction", "target", "output_format", "instruction")

    @model_validator(mode="after")
    def _sync_sections(self) -> "AgentPromptModel":
        """确保经典字段和 sections dict 双向同步。

        经典字段优先：如果字段有值，会覆盖 sections 中的同名 key。
        few_shot_examples 不参与 sections 同步（类型为 List，单独处理）。
        """
        for name in self._NAMED_STR_FIELDS:
            value = getattr(self, name)
            if value is not None:
                self.sections[name] = value
            elif name in self.sections:
                setattr(self, name, self.sections[name])
        return self

    # ── 核心方法 ──────────────────────────────────────────────

    def get_section(self, name: str) -> Optional[str]:
        """获取指定 section 的内容（str 类型 section）。"""
        if name in self._NAMED_STR_FIELDS:
            return getattr(self, name)
        return self.sections.get(name)

    def set_section(
        self,
        name: str,
        content: str,
        message_type: ChatMessageEnum = ChatMessageEnum.SYSTEM,
    ) -> None:
        """设置一个 str 类型的 section（经典字段或自定义）。"""
        if name in self._NAMED_STR_FIELDS:
            setattr(self, name, content)
        self.sections[name] = content
        self.message_type_mapping[name] = message_type

    def get_message_type(self, section_name: str) -> ChatMessageEnum:
        """获取指定 section 对应的 message 角色类型。

        Args:
            section_name: section 名称。

        Returns:
            对应的 ChatMessageEnum，默认为 HUMAN。
        """
        return self.message_type_mapping.get(section_name, ChatMessageEnum.HUMAN)

    def to_messages(
        self,
        assemble_order: Optional[List[str]] = None,
    ) -> List[Message]:
        """按指定顺序将 sections 转为 Message 列表。

        few_shot_examples 会被展开为交替的 HUMAN/AI message 对。

        Args:
            assemble_order: section 名称的有序列表，决定输出顺序。
                未指定时使用 DEFAULT_ASSEMBLE_ORDER + 自定义 sections 的插入顺序。

        Returns:
            非空 section 对应的 Message 列表。
        """
        if assemble_order is None:
            classic = [k for k in DEFAULT_ASSEMBLE_ORDER if self._has_content(k)]
            custom = [
                k for k in self.sections
                if k not in DEFAULT_ASSEMBLE_ORDER and self.sections[k]
            ]
            assemble_order = classic + custom

        messages = []
        for name in assemble_order:
            # few_shot_examples 特殊处理：展开为多条 message
            if name == "few_shot_examples":
                messages.extend(self._expand_few_shot())
                continue

            content = self.sections.get(name)
            if not content:
                continue
            msg_type = self.get_message_type(name)
            messages.append(Message(type=msg_type, content=content))
        return messages

    def _has_content(self, name: str) -> bool:
        """检查某个 section 是否有内容。"""
        if name == "few_shot_examples":
            return bool(self.few_shot_examples)
        return bool(self.sections.get(name))

    def _expand_few_shot(self) -> List[Message]:
        """将 few_shot_examples 展开为 HUMAN / AI 交替的 Message 列表。"""
        if not self.few_shot_examples:
            return []
        messages = []
        for example in self.few_shot_examples:
            messages.append(Message(type=ChatMessageEnum.HUMAN, content=example.input))
            messages.append(Message(type=ChatMessageEnum.AI, content=example.output))
        return messages


    def __add__(self, other: "AgentPromptModel") -> "AgentPromptModel":
        """合并两个 AgentPromptModel，self 的非空值优先。

        few_shot_examples 合并策略：self 有则用 self，否则用 other。
        """
        merged_sections = {**other.sections, **{
            k: v for k, v in self.sections.items() if v
        }}
        merged_mapping = {**other.message_type_mapping, **self.message_type_mapping}

        # 经典 str 字段不放进 sections 参数（由 _sync_sections 自动同步）
        all_named = set(self._NAMED_STR_FIELDS) | {"few_shot_examples"}

        return AgentPromptModel(
            introduction=self.introduction or other.introduction,
            target=self.target or other.target,
            few_shot_examples=self.few_shot_examples or other.few_shot_examples,
            output_format=self.output_format or other.output_format,
            instruction=self.instruction or other.instruction,
            sections={
                k: v for k, v in merged_sections.items()
                if k not in all_named
            },
            message_type_mapping=merged_mapping,
        )

    def __bool__(self) -> bool:
        """任意 section 或 few_shot_examples 有内容即为 True。"""
        return any(self.sections.values()) or bool(self.few_shot_examples)