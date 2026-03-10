# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_dto.py
from typing import Optional, Any, Dict

from pydantic import BaseModel, Field, model_serializer, model_validator

from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.planner_dto import PlannerDTO
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

    # Legacy field for backward compatibility with magent-ui
    _planner: Optional[PlannerDTO] = None

    @property
    def planner(self) -> Optional[PlannerDTO]:
        """Get planner from agent_type fields."""
        if self.agent_type:
            return PlannerDTO(
                id=f"{self.agent_type}_planner",
                nickname='',
                workflow_id=self.workflow_id,
                members=self.members if self.members else []
            )
        return self._planner

    @planner.setter
    def planner(self, value: Optional[PlannerDTO]) -> None:
        """Set planner and update agent_type fields."""
        self._planner = value
        if value:
            # Convert planner to agent_type fields
            if value.id:
                self.agent_type = value.id.replace('_planner', '')
            if value.workflow_id:
                self.workflow_id = value.workflow_id
            if value.members:
                self.members = value.members

    @model_validator(mode='before')
    @classmethod
    def convert_planner_to_agent_type(cls, data: Any) -> Any:
        """Convert legacy planner field to new agent_type fields when receiving data from UI."""
        if isinstance(data, dict):
            planner = data.get('planner')
            if planner:
                # If planner is provided, convert it to new fields
                if isinstance(planner, dict):
                    planner_id = planner.get('id', '')
                    # Convert planner_id to agent_type: 'workflow_planner' -> 'workflow'
                    if planner_id:
                        data['agent_type'] = planner_id.replace('_planner', '')
                    if 'workflow_id' in planner:
                        data['workflow_id'] = planner['workflow_id']
                    if 'members' in planner:
                        data['members'] = planner['members']
                elif hasattr(planner, 'id'):
                    # PlannerDTO object
                    data['agent_type'] = planner.id.replace('_planner', '')
                    if planner.workflow_id:
                        data['workflow_id'] = planner.workflow_id
                    if planner.members:
                        data['members'] = planner.members
        return data

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Custom serializer to include planner field for UI compatibility."""
        # Get default serialization
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'description': self.description,
            'opening_speech': self.opening_speech,
            'prompt': self.prompt,
            'llm': self.llm,
            'tool': self.tool,
            'memory': self.memory,
            'agent_type': self.agent_type,
            'workflow_id': self.workflow_id,
            'members': self.members,
            'knowledge': self.knowledge,
            'mtime': self.mtime,
        }

        # Generate planner field from agent_type for backward compatibility
        if self.agent_type:
            planner_id = f"{self.agent_type}_planner"
            data['planner'] = {
                'id': planner_id,
                'nickname': '',
                'workflow_id': self.workflow_id,
                'members': self.members if self.members else []
            }

        return data
