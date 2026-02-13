# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/5 17:43
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: conversation_message.py

import uuid
from typing import Optional

from pydantic import Field

from agentuniverse.agent.memory.message import Message
from agentuniverse.base.context.framework_context_manager import \
    FrameworkContextManager


class ConversationMessage(Message):
    """
    The basic class for conversation memory message

    Attributes:
        id (Optional[str]): Unique identifier.
        trace_id (Optional[str]): Trace ID.
        conversation_id (Optional[str]): Conversation ID.
        source (Optional[str]): Message source.
        source_type (Optional[str]): Type of the message source.
        target (Optional[str]): Message target.
        target_type (Optional[str]): Type of the message target.
        type (Optional[str]): Message type.
        content (Optional[str]): Message content.
        metadata (Optional[dict]): The metadata of the message.
    """
    id: Optional[str | int] = Field(default_factory=lambda: uuid.uuid4().hex)
    trace_id: Optional[str] = None
    conversation_id: Optional[str] = None
    source_type: Optional[str] = None
    target: Optional[str] = None
    target_type: Optional[str] = None
    content: Optional[str] = None
    additional_args: Optional[dict] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        """Convert the dict to ConversationMessage."""
        if "type" not in data and "role" in data:
            data = {**data, "type": data.pop("role")}
        return cls.model_validate(data)

    @classmethod
    def from_message(cls, message: Message, session_id: str):
        if not message.metadata:
            message.metadata = {}
        message.metadata['prefix'] = '之前对话的摘要：' if message.type == 'summarize' else ''
        message.metadata['params'] = "{}"
        trace_id = message.metadata.get('trace_id')
        if not trace_id:
            trace_id = FrameworkContextManager().get_context('trace_id')
            message.metadata['trace_id'] = trace_id
        # 将 content 统一转为 str，兼容父类 ContentT 可能为 list 的情况
        content = message.content_text if not isinstance(message.content, str) else message.content
        return cls(
            id=uuid.uuid4().hex,
            content=content,
            metadata=message.metadata,
            type=message.type,
            source=message.source,
            source_type='agent',
            target=message.source,
            target_type='agent',
            trace_id=trace_id,
            conversation_id=message.metadata.get('session_id') if not session_id else session_id,
        )

    @classmethod
    def check_and_convert_message(cls, messages, session_id: str = None):
        if len(messages) == 0:
            return []
        message = messages[0]
        if isinstance(message, cls):
            return messages
        if isinstance(message, Message):
            return [cls.from_message(m, session_id) for m in messages]
