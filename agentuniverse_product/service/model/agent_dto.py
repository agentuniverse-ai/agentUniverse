# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_dto.py
from typing import Optional

from pydantic import BaseModel, Field

from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.prompt_dto import PromptDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO


class AgentDTO(BaseModel):
    id: str = Field(description="ID")
    nickname: Optional[str] = Field(description="agent nickname", default="")
    avatar: Optional[str] = Field(description="agent avatar path", default="")
    description: Optional[str] = Field(description="agent description", default="")
    opening_speech: Optional[str] = Field(description="agent opening speech", default="")
    prompt: Optional[PromptDTO] = Field(description="agent prompt", default=None)
    llm: Optional[LlmDTO] = Field(description="agent llm", default=None)
    tool: Optional[list[ToolDTO]] = Field(description="agent tool list", default=[])
    memory: Optional[str] = Field(description="agent memory id", default='')
    agent_type: Optional[str] = Field(description="agent type: react/rag/peer/workflow", default=None)
    workflow_id: Optional[str] = Field(description="workflow id for workflow agents", default=None)
    members: Optional[list] = Field(description="peer agent members", default=None)
    knowledge: Optional[list[KnowledgeDTO]] = Field(description="agent knowledge list", default=[])
    mtime: Optional[float] = Field(description="product last modification time.", default=None)
