# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/25 17:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_util.py
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger
from agentuniverse.base.util.memory_util import get_memory_string


def assemble_memory_input(memory: Memory, agent_input: dict, query_params: dict = None) -> list[Message]:
    """Assemble memory information for the agent input parameters.

    Args:
        memory (Memory): The memory instance.
        agent_input (dict): Agent input parameters for the agent.

    Returns:
        list[Message]: The retrieved memory messages.
    """
    memory_messages = []
    if memory:
        # get the memory messages from the memory instance.
        if not query_params:
            memory_messages = memory.get(**agent_input)
        else:
            memory_messages = memory.get(**query_params)
        # convert the memory messages to a string and add it to the agent input object.
        memory_str = get_memory_string(memory_messages, agent_input.get("agent_id"))
        agent_input[memory.memory_key] = memory_str
    return memory_messages


def assemble_memory_output(
    memory: Memory, agent_input: dict, content: str, source: str = None, memory_messages=None
) -> list[Message]:
    """Assemble the historical memory information and current memory information
     into the agent's final output memory information.

    Args:
        memory (Memory): The current memory instance.
        agent_input (dict): Agent input object.
        content (str): The content of the current memory message.
        source (str): The source of the current memory message.
        memory_messages (List[Message]): The historical memory messages.
    Returns:
        list[Message]: The assembled final output memory information.
    """
    cur_memory_message = Message(content=content, source=source)
    if memory:
        # add the current memory message to the memory instance.
        memory.add([cur_memory_message], **agent_input)
    if memory_messages is None:
        memory_messages = []
    memory_messages.append(cur_memory_message)
    return memory_messages


def process_agent_llm_config(agent_id: str, agent_profile: dict, default_llm_configer: DefaultLLMConfiger) -> dict:
    """
    Update the LLM model name in the agent's profile based on the default LLM configuration.

    If the agent's profile does not specify an LLM
    model name, and if a default LLM is provided by default LLM configuration, the profile will
    be updated accordingly.
    """
    if not agent_id or default_llm_configer is None:
        return agent_profile

    if not agent_profile:
        agent_profile = {}

    llm_model = agent_profile.setdefault("llm_model", {})
    llm_name = llm_model.get("name")

    # If LLM model name is specified, return the agent profile unchanged
    if llm_name:
        return agent_profile

    # Update the LLM model name with the default LLM from the config manager, if available
    if default_llm_configer.default_llm:
        llm_model["name"] = default_llm_configer.default_llm

    # Return the updated agent profile
    return agent_profile
