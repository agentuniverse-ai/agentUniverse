# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/11/15 11:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_util.py
from agentuniverse.prompt.chat_prompt import ChatPrompt


def convert_prompt_to_message(agent_input: dict, prompt: ChatPrompt) -> list:
    """Convert a ChatPrompt into a list of role/content message dicts.

    Args:
        agent_input: Input dict used to format human/user message content.
        prompt: The chat prompt whose messages are converted.

    Returns:
        list: Message dicts with 'role' ('system' or 'user') and 'content' keys.
    """
    messages = prompt.messages
    prompt_list = []
    for message in messages:
        if message.type == 'system':
            prompt_list.append({'role': 'system', 'content': message.content})
        if message.type == 'human' or message.type == 'user':
            formatted_content = message.content.format(**agent_input)
            prompt_list.append({'role': 'user', 'content': formatted_content})
    return prompt_list


def get_prompt_str(agent_input: dict, prompt: ChatPrompt) -> str:
    """Render a ChatPrompt's messages into a single readable text block.

    Args:
        agent_input: Input dict used to format human/user message content.
        prompt: The chat prompt whose messages are rendered.

    Returns:
        str: Each message prefixed with 'System prompt:' or 'User prompt:'.
    """
    messages = prompt.messages
    prompt_str = ''
    for message in messages:
        if message.type == 'system':
            prompt_str += f"System prompt: {message.content}\n\n"
        if message.type == 'human' or message.type == 'user':
            formatted_content = message.content.format(**agent_input)
            prompt_str += f"User prompt: {formatted_content}\n\n"
    return prompt_str
