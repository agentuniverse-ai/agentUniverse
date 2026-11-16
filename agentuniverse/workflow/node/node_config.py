# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/21 11:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_config.py
from typing import Optional, List, Any, Union

from pydantic import BaseModel


class NodeOutputParams(BaseModel):
    """Represent an output parameter produced by a workflow node.

    Attributes:
        name: Name of the output parameter.
        type: Data type of the output parameter.
        value: Value carried by the output parameter.
    """

    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None


class InputValueParams(BaseModel):
    """Represent the value configuration of a node input.

    Attributes:
        type: Type of the configured input value.
        content: Text or list content supplied as the input value.
    """

    type: Optional[str] = None
    content: Optional[Union[List, str]] = None


class NodeInputParams(BaseModel):
    """Represent an input parameter consumed by a workflow node.

    Attributes:
        name: Name of the input parameter.
        type: Data type of the input parameter.
        value: Value configuration associated with the input parameter.
    """

    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[InputValueParams] = None


class NodeInfoParams(BaseModel):
    """Represent identifying information for a workflow component.

    Attributes:
        name: Name of the referenced component or parameter.
        type: Type of the referenced component or parameter.
        value: Additional value associated with the reference.
    """

    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Any] = None


class ToolNodeInputParams(BaseModel):
    """Define the input configuration for a tool node.

    Attributes:
        tool_param: Tool-specific configuration parameters.
        input_param: Input parameters passed to the tool node.
    """

    tool_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class KnowledgeNodeInputParams(BaseModel):
    """Define the input configuration for a knowledge node.

    Attributes:
        knowledge_param: Knowledge-component configuration parameters.
        input_param: Input parameters passed to the knowledge node.
    """

    knowledge_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class AgentNodeInputParams(BaseModel):
    """Define the input configuration for an agent node.

    Attributes:
        agent_param: Agent-specific configuration parameters.
        input_param: Input parameters passed to the agent node.
    """

    agent_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class LLMNodeInputParams(BaseModel):
    """Define the input configuration for an LLM node.

    Attributes:
        llm_param: LLM-specific configuration parameters.
        input_param: Input parameters passed to the LLM node.
    """

    llm_param: Optional[List[NodeInfoParams]] = list()
    input_param: Optional[List[NodeInputParams]] = list()


class EndNodeInputParams(BaseModel):
    """Define the input configuration for an end node.

    Attributes:
        input_param: Input parameters passed to the end node.
        prompt: Optional prompt configuration used by the end node.
    """

    input_param: Optional[List[NodeInputParams]] = list()
    prompt: Optional[NodeInfoParams] = None


class ConditionParams(BaseModel):
    """Represent a comparison condition in a conditional node.

    Attributes:
        compare: Comparison operator applied by the condition.
        left: Left-hand input of the comparison.
        right: Right-hand input of the comparison.
    """

    compare: Optional[str] = None
    left: Optional[NodeInputParams] = None
    right: Optional[NodeInputParams] = None


class ConditionBranchParams(BaseModel):
    """Represent a named branch and its conditions.

    Attributes:
        name: Name of the conditional branch.
        conditions: Conditions that determine whether the branch is selected.
    """

    name: Optional[str] = None
    conditions: Optional[List[ConditionParams]] = list()


class ConditionNodeInputParams(BaseModel):
    """Define the branch configuration for a conditional node.

    Attributes:
        branches: Conditional branches available to the node.
    """

    branches: Optional[List[ConditionBranchParams]] = list()
