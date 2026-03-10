# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/23 14:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_util.py
import copy
import os

from typing import Dict, List, Optional

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.default.workflow_agent.workflow_agent import WorkflowAgent
from agentuniverse.agent.template.peer_agent_template import PeerAgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.agent.template.react_agent_template import ReActAgentTemplate
from agentuniverse.base.component.component_configer_util import ComponentConfigerUtil
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse_product.base.product import Product
from agentuniverse_product.base.product_configer import ProductConfiger
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.base.util.yaml_util import update_nested_yaml_value
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.knowledge_dto import KnowledgeDTO
from agentuniverse_product.service.model.llm_dto import LlmDTO
from agentuniverse_product.service.model.prompt_dto import PromptDTO
from agentuniverse_product.service.model.tool_dto import ToolDTO


def assemble_product_config_data(agent_dto: AgentDTO) -> Dict:
    """Assemble the agent product configuration data.

    Args:
        agent_dto (AgentDTO): The agent DTO.

    Returns:
        Dict: The assembled agent product configuration data.
    """
    return {
        'id': agent_dto.id,
        'nickname': agent_dto.nickname,
        'avatar': agent_dto.avatar,
        'opening_speech': agent_dto.opening_speech,
        'type': 'AGENT',
        'metadata': {
            'class': 'AgentProduct',
            'module': 'agentuniverse_product.base.agent_product',
            'type': 'PRODUCT'
        }
    }


def validate_create_agent_parameters(agent_dto: AgentDTO) -> None:
    """Validate the parameters for creating an agent.

    Args:
        agent_dto (AgentDTO): The agent DTO.
    """
    if agent_dto.id is None:
        raise ValueError("Agent id cannot be None.")
    agent = AgentManager().get_instance_obj(agent_dto.id, new_instance=False)
    if agent:
        raise ValueError("Agent instance corresponding to the agent id already exists.")
    if agent_dto.agent_type is None:
        raise ValueError("The agent_type in agent cannot be None.")
    if agent_dto.agent_type != 'workflow':
        if agent_dto.prompt is None:
            raise ValueError("The prompt in agent cannot be None.")
        if agent_dto.llm is None:
            raise ValueError("The llm in agent cannot be None.")


def assemble_agent_config_data(agent_dto: AgentDTO) -> Dict:
    """Assemble the agent configuration data.

    Args:
        agent_dto (AgentDTO): The agent DTO.

    Returns:
        Dict: The assembled agent configuration data.
    """
    agent_config_data = {
        'info': {
            'name': agent_dto.id,
            'description': agent_dto.description
        },
        'profile': {
        },
        'action': {}
    }
    if agent_dto.workflow_id:
        agent_config_data['profile']['workflow_id'] = agent_dto.workflow_id

    if agent_dto.llm:
        llm = LLMManager().get_instance_obj(agent_dto.llm.id, new_instance=False)
        if llm is None:
            raise ValueError("The llm instance corresponding to the llm id cannot be found.")
        llm_model_dict = {'name': agent_dto.llm.id}
        if agent_dto.llm.temperature:
            llm_model_dict['temperature'] = agent_dto.llm.temperature
        if agent_dto.llm.model_name:
            llm_model_dict['model_name'] = agent_dto.llm.model_name[0]
        agent_config_data['profile']['llm_model'] = llm_model_dict

    if agent_dto.tool:
        agent_config_data['action']['tool'] = [tool.id for tool in agent_dto.tool]

    if agent_dto.knowledge:
        agent_config_data['action']['knowledge'] = [knowledge.id for knowledge in agent_dto.knowledge]

    if agent_dto.agent_type == 'workflow':
        metadata_class = 'WorkflowAgent'
        metadata_agent_path = 'workflow_agent'
    elif agent_dto.agent_type == 'react':
        metadata_class = 'ReActAgent'
        metadata_agent_path = 'react_agent'
        agent_config_data['profile']['prompt_version'] = 'default_react_agent.cn'
    elif agent_dto.agent_type == 'peer':
        metadata_class = 'PeerAgent'
        metadata_agent_path = 'peer_agent'
    else:
        metadata_class = 'RagAgent'
        metadata_agent_path = 'rag_agent'
        agent_config_data['profile']['prompt_version'] = 'default_rag_agent.cn'

    agent_config_data['metadata'] = {
        'class': metadata_class,
        'module': f'agentuniverse.agent.default.{metadata_agent_path}.{metadata_agent_path}',
        'type': 'AGENT'
    }
    return agent_config_data


def register_agent(file_path: str):
    """Register the agent instance to the agent manager.

    Args:
        file_path (str): The file path of the agent configuration.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    agent_configer: AgentConfiger = AgentConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(agent_configer)
    component_instance: Agent = component_clz().initialize_by_component_configer(agent_configer)
    component_instance.component_config_path = component_configer.configer.path
    AgentManager().register(component_instance.get_instance_code(), component_instance)


def register_product(file_path: str):
    """Register the product instance to the product manager.

    Args:
        file_path (str): The file path of the product configuration.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    product_configer: ProductConfiger = ProductConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(product_configer)
    component_instance: Product = component_clz().initialize_by_component_configer(product_configer)
    component_instance.component_config_path = component_configer.configer.path
    ProductManager().register(component_instance.get_instance_code(), component_instance)


def unregister_product(file_path: str):
    """Unregister the product instance from the product manager.

    Args:
        file_path (str): The file path of the product configuration.
    """
    absolute_file_path = os.path.abspath(file_path)
    configer = Configer(path=absolute_file_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    product_configer: ProductConfiger = ProductConfiger().load_by_configer(component_configer.configer)
    component_clz = ComponentConfigerUtil.get_component_object_clz_by_component_configer(product_configer)
    component_instance: Product = component_clz().initialize_by_component_configer(product_configer)
    ProductManager().unregister(component_instance.get_instance_code())


def get_agent_type(agent: Agent) -> str:
    """Return the agent type string based on the agent's template class.

    Args:
        agent (Agent): The agent instance.

    Returns:
        str: The agent type ('react', 'rag', 'peer', 'workflow', or '').
    """
    if not agent:
        return ''
    if isinstance(agent, WorkflowAgent):
        return 'workflow'
    if isinstance(agent, PeerAgentTemplate):
        return 'peer'
    if isinstance(agent, ReActAgentTemplate):
        return 'react'
    if isinstance(agent, RagAgentTemplate):
        return 'rag'
    return ''


def get_peer_members(agent: Agent) -> Optional[List[AgentDTO]]:
    """Get peer agent members from agent profile.

    Args:
        agent (Agent): The agent instance (should be a PeerAgentTemplate).

    Returns:
        Optional[List[AgentDTO]]: List of member AgentDTOs, or None if not a peer agent.
    """
    if not isinstance(agent, PeerAgentTemplate):
        return None
    agent_model: AgentModel = agent.agent_model
    member_keys = ['planning', 'executing', 'expressing', 'reviewing']
    default_member_names = ['PlanningAgent', 'ExecutingAgent', 'ExpressingAgent', 'ReviewingAgent']
    members = []
    try:
        profile = copy.deepcopy(agent_model.profile)
        for i, member_key in enumerate(member_keys):
            profile.setdefault(member_key, default_member_names[i])
        for member_key in member_keys:
            member_name = profile.get(member_key)
            if not member_name:
                continue
            if isinstance(member_name, str):
                member_name = [member_name]
            for name in member_name:
                member_agent: Agent = AgentManager().get_instance_obj(name)
                product: Product = ProductManager().get_instance_obj(name)
                if member_agent:
                    agent_dto = AgentDTO(id=name,
                                         nickname=product.nickname if product else '',
                                         avatar=product.avatar if product else '')
                    members.append(assemble_agent_dto(member_agent, agent_dto))
    except Exception:
        return []
    return members


def assemble_agent_dto(agent: Agent, agent_dto: AgentDTO) -> AgentDTO:
    """Assemble agent dto from agent instance."""
    agent_model: AgentModel = agent.agent_model
    agent_dto.description = agent_model.info.get('description', '')
    agent_dto.prompt = get_prompt_dto(agent_model)
    agent_dto.llm = get_llm_dto(agent_model)
    agent_dto.memory = agent_model.memory.get('name', '')
    agent_dto.tool = get_tool_dto_list(agent_model)
    agent_dto.knowledge = get_knowledge_dto_list(agent_model)
    agent_dto.agent_type = get_agent_type(agent)
    agent_dto.workflow_id = agent_model.profile.get('workflow_id')
    agent_dto.members = get_peer_members(agent)
    return agent_dto


def get_knowledge_dto_list(agent_model: AgentModel) -> List[KnowledgeDTO]:
    """Get knowledge dto list."""
    knowledge_name_list = agent_model.action.get('knowledge', [])
    res = []
    if not knowledge_name_list:
        return res
    for knowledge_name in knowledge_name_list:
        product: Product = ProductManager().get_instance_obj(knowledge_name, new_instance=False)
        knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name, new_instance=False)
        if knowledge is None:
            continue
        knowledge_dto = KnowledgeDTO(nickname=product.nickname if product else '', id=knowledge_name)
        knowledge_dto.description = knowledge.description
        res.append(knowledge_dto)
    return res


def get_tool_dto_list(agent_model: AgentModel) -> List[ToolDTO]:
    """Get tool dto list."""
    tool_name_list = agent_model.action.get('tool', [])
    res = []
    if len(tool_name_list) < 1:
        return res
    for tool_name in tool_name_list:
        product: Product = ProductManager().get_instance_obj(tool_name, new_instance=False)
        tool: Tool = ToolManager().get_instance_obj(tool_name, new_instance=False)
        tool_dto = ToolDTO(nickname=product.nickname if product is not None else '',
                           avatar=product.avatar if product is not None else '',
                           id=tool.name)
        tool_dto.description = tool.description
        res.append(tool_dto)
    return res


def get_prompt_dto(agent_model: AgentModel) -> PromptDTO | None:
    """Get prompt dto."""
    profile_prompt_model: AgentPromptModel = AgentPromptModel(
        introduction=agent_model.profile.get('introduction'),
        target=agent_model.profile.get('target'),
        instruction=agent_model.profile.get('instruction'))

    prompt_version = agent_model.profile.get('prompt_version')
    version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

    if version_prompt:
        version_prompt_model: AgentPromptModel = AgentPromptModel(
            introduction=getattr(version_prompt, 'introduction', ''),
            target=getattr(version_prompt, 'target', ''),
            instruction=getattr(version_prompt, 'instruction', ''))
        profile_prompt_model = profile_prompt_model + version_prompt_model
    if not profile_prompt_model:
        return None
    return PromptDTO(introduction=profile_prompt_model.introduction, target=profile_prompt_model.target,
                     instruction=profile_prompt_model.instruction)


def get_llm_dto(agent_model: AgentModel) -> LlmDTO | None:
    """Get llm dto from agent."""
    llm_model = agent_model.profile.get('llm_model', {})
    llm_id = llm_model.get('name')
    llm: LLM = LLMManager().get_instance_obj(llm_id)
    product: Product = ProductManager().get_instance_obj(llm_id)
    if llm is None:
        return None
    llm_model_name = llm_model.get('model_name') if llm_model.get('model_name') else llm.model_name
    llm_temperature = llm_model.get('temperature') if llm_model.get('temperature') else llm.temperature
    return LlmDTO(id=llm_id, nickname=product.nickname if product else '', temperature=llm_temperature,
                  model_name=[llm_model_name])


def update_agent_config(agent: Agent, agent_dto: AgentDTO, agent_config_path: str) -> None:
    """Update agent instance and configuration yaml file."""
    agent_updates = {}
    if agent_dto.description is not None and agent_dto.description != "":
        agent_updates['info.description'] = agent_dto.description
        agent.agent_model.info['description'] = agent_dto.description
    if agent_dto.prompt is not None:
        prompt_dto = agent_dto.prompt
        if prompt_dto.target is not None:
            agent_updates['profile.target'] = agent_dto.prompt.target
            agent.agent_model.profile['target'] = agent_dto.prompt.target
        if prompt_dto.introduction is not None:
            agent_updates['profile.introduction'] = agent_dto.prompt.introduction
            agent.agent_model.profile['introduction'] = agent_dto.prompt.introduction
        if prompt_dto.instruction is not None:
            agent_updates['profile.instruction'] = agent_dto.prompt.instruction
            agent.agent_model.profile['instruction'] = agent_dto.prompt.instruction
    if agent_dto.llm is not None:
        llm_dto = agent_dto.llm
        if hasattr(agent, 'llm_name'):
            agent.llm_name = agent_dto.llm.id
        if llm_dto.id:
            agent_updates['profile.llm_model.name'] = agent_dto.llm.id
            agent.agent_model.profile.get('llm_model')['name'] = agent_dto.llm.id
        if llm_dto.temperature:
            agent_updates['profile.llm_model.temperature'] = agent_dto.llm.temperature
            agent.agent_model.profile.get('llm_model')['temperature'] = agent_dto.llm.temperature
        if llm_dto.model_name:
            agent_updates['profile.llm_model.model_name'] = agent_dto.llm.model_name[0]
            agent.agent_model.profile.get('llm_model')['model_name'] = agent_dto.llm.model_name[0]
        if not llm_dto.model_name:
            llm: LLM = LLMManager().get_instance_obj(llm_dto.id)
            llm_model = agent.agent_model.profile.get('llm_model', {})
            llm_model.pop('model_name', None)
            agent_updates['profile.llm_model.model_name'] = llm.model_name

    if agent_dto.tool is not None:
        tool_dto_list: List[ToolDTO] = agent_dto.tool
        tool_name_list = [tool_dto.id for tool_dto in tool_dto_list]
        if hasattr(agent, 'tool_names'):
            agent.tool_names = tool_name_list
        agent_updates['action.tool'] = tool_name_list
        agent.agent_model.action['tool'] = tool_name_list
    if agent_dto.knowledge is not None:
        knowledge_dto_list: List[KnowledgeDTO] = agent_dto.knowledge
        knowledge_name_list = [knowledge_dto.id for knowledge_dto in knowledge_dto_list]
        if hasattr(agent, 'knowledge_names'):
            agent.knowledge_names = knowledge_name_list
        agent_updates['action.knowledge'] = knowledge_name_list
        agent.agent_model.action['knowledge'] = knowledge_name_list
    if agent_updates:
        update_nested_yaml_value(agent_config_path, agent_updates)


def update_agent_product_config(agent_product: Product, agent_dto: AgentDTO, product_config_path: str) -> None:
    """Update agent product instance and configuration yaml file."""
    if agent_dto is None or agent_dto.opening_speech is None:
        return
    agent_product.opening_speech = agent_dto.opening_speech
    update_nested_yaml_value(product_config_path, {'opening_speech': agent_dto.opening_speech})


def assemble_tool_input(agent: Agent, agent_input: str) -> dict:
    """Assemble tool input parameters for the agent invocation.

    Args:
        agent (Agent): The agent instance.
        agent_input (str): The agent input string.

    Returns:
        dict: The tool input parameters dictionary.
    """
    tool_id_list = agent.agent_model.action.get('tool', [])
    tool_input_dict = {}
    for tool_id in tool_id_list:
        tool: Tool = ToolManager().get_instance_obj(tool_id)
        if tool is None:
            continue
        if len(tool.input_keys) > 0:
            input_key = tool.input_keys[0]
            tool_input_dict[input_key] = agent_input
    return tool_input_dict


def validate_and_assemble_agent_input(agent_id: str, session_id: str, input: str, chat_history: list = None) -> dict:
    """Validate and assemble agent input.

    Args:
        agent_id (str): The agent id.
        session_id (str): The session id.
        input (str): The agent input string.
        chat_history (list): The chat history list.

    Returns:
        dict: The agent input dictionary.
    """
    if agent_id is None or session_id is None:
        raise ValueError("Agent id or session id cannot be None.")
    agent: Agent = AgentManager().get_instance_obj(agent_id)
    if agent is None:
        raise ValueError("The agent instance corresponding to the agent id cannot be found.")
    tool_input_dict = assemble_tool_input(agent, input)

    memory_name = agent.agent_model.memory.get('name', '')

    agent_input_dict = {
        'input': input,
        'chat_history': None if memory_name else get_chat_history_str(chat_history),
        'agent_id': agent_id,
        'session_id': session_id
    }

    agent_input_dict.update(tool_input_dict)

    return agent_input_dict


def get_chat_history_str(messages: List[dict]) -> str:
    string_messages = []
    for m in messages:
        if m.get('type') == 'system':
            role = 'System'
        elif m.get('type') == 'human':
            role = 'Human'
        elif m.get('type') == 'ai':
            role = "AI"
        else:
            role = ""
        m_str = ""
        if role:
            m_str += f"Message role: {role} "
        m_str += f"Message content: \n {m.get('content', '')} "
        string_messages.append(m_str)
    return "\n\n".join(string_messages)
