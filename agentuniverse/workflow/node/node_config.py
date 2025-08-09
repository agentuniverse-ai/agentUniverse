# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 11:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_config.py
from typing import Optional, List, Any, Union

from pydantic import BaseModel


class NodeOutputParams(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None


class InputValueParams(BaseModel):
    type: Optional[str] = None
    content: Optional[Union[List, str]] = None


class NodeInputParams(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[InputValueParams] = None


class NodeInfoParams(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None


class ToolNodeInputParams(BaseModel):
    tool_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class KnowledgeNodeInputParams(BaseModel):
    knowledge_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class AgentNodeInputParams(BaseModel):
    agent_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class LLMNodeInputParams(BaseModel):
    llm_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class EndNodeInputParams(BaseModel):
    input_param: Optional[List[NodeInputParams]] = list()
    prompt: Optional[NodeInfoParams] = None


class ConditionParams(BaseModel):
    compare: Optional[str] = None
    left: Optional[NodeInputParams] = None
    right: Optional[NodeInputParams] = None


class ConditionBranchParams(BaseModel):
    name: Optional[str] = None
    conditions: Optional[List[ConditionParams]] = list()


class ConditionNodeInputParams(BaseModel):
    branches: Optional[List[ConditionBranchParams]] = list()
