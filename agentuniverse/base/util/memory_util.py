# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/27 11:37
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: memory_util.py
from typing import List, Optional

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


def generate_messages(memories: list) -> List[Message]:
    """ Generate a list of messages from the given memories

    Args:
        memories(list): List of memory objects, which can be of type str, dict or Message.

    Returns:
        List[Message]: List of messages
    """
    messages = []
    for m in memories:
        if isinstance(m, Message):
            messages.append(m)
        elif isinstance(m, dict):
            messages.append(Message.from_dict(m))
        elif isinstance(m, str):
            messages.append(Message(
                type=ChatMessageEnum.HUMAN,
                content=m,
                metadata={}
            ))
    return messages


def generate_memories(chat_messages) -> list:
    return [
        {"content": message.content, "type": 'ai' if message.type == 'AIMessageChunk' else message.type}
        for message in chat_messages.messages
    ] if chat_messages.messages else []


def _extract_text_content(content) -> str:
    """Extract plain text from ContentT (str or multimodal list).

    Args:
        content: Message content, either str or List[Union[str, Dict]].

    Returns:
        str: Extracted text content.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    # multimodal content list
    parts = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict) and item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "".join(parts)


def get_memory_string(messages: List[Message], agent_id: Optional[str] = None) -> str:
    """Convert the given messages to a string.

    Args:
        messages: The list of messages.
        agent_id: Optional agent id for replacing agent references.

    Returns:
        str: The string representation of the messages.
    """
    current_trace_id = FrameworkContextManager().get_context("trace_id")
    string_messages = []

    for m in messages:
        msg_type = m.type
        text_content = _extract_text_content(m.content)

        # Handle INPUT/OUTPUT types with special formatting
        if msg_type in (ChatMessageEnum.INPUT.value, ChatMessageEnum.OUTPUT.value):
            trace_id = getattr(m, 'trace_id', None)
            if current_trace_id and current_trace_id == trace_id:
                continue
            role: str = (m.metadata or {}).get('prefix', "")
            if agent_id:
                role = role.replace(f"智能体 {agent_id}", " 你")
                role = role.replace(f"Agent {agent_id}", " You")
            timestamp = (m.metadata or {}).get('timestamp', "")
            string_messages.append(f"{timestamp} {role}:{text_content}")
            continue

        # Standard role mapping
        role_map = {
            ChatMessageEnum.SYSTEM.value: "System",
            ChatMessageEnum.HUMAN.value: "Human",
            ChatMessageEnum.USER.value: "Human",
            ChatMessageEnum.AI.value: "AI",
            ChatMessageEnum.ASSISTANT.value: "AI",
            ChatMessageEnum.TOOL.value: "Tool",
        }
        role = role_map.get(msg_type, "")

        parts = []
        if m.metadata and m.metadata.get('gmt_created'):
            parts.append(m.metadata['gmt_created'])
        if m.source:
            parts.append(f"Message source: {m.source}")
        if role:
            parts.append(f"Message role: {role}")
        parts.append(f":{text_content}")

        # Append tool call info if present
        if m.has_tool_calls() and m.tool_calls:
            tool_info = ", ".join(
                f"{tc.function.name}({tc.function.arguments})"
                for tc in m.tool_calls
            )
            parts.append(f"[Tool calls: {tool_info}]")

        string_messages.append(" ".join(parts))

    return "\n\n".join(string_messages)


def get_memory_tokens(memories: List[Message], llm_name: str = None) -> int:
    """Get the number of tokens in the given memories.

    Args:
        memories: The list of messages.
        llm_name: The name of the LLM to use for token counting.

    Returns:
        int: The number of tokens in the given memories.
    """
    memory_str = get_memory_string(memories)
    llm_instance: LLM = LLMManager().get_instance_obj(llm_name)
    return llm_instance.get_num_tokens(memory_str) if llm_instance else len(memory_str)
