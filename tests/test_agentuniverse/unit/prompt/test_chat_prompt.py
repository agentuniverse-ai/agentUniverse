# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_chat_prompt.py
"""Unit tests for ChatPrompt."""

import pytest

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt_model import AgentPromptModel
from langchain_core.prompts import ChatPromptTemplate


class TestChatPrompt:
    def test_default_messages_empty(self):
        assert ChatPrompt().messages == []

    def test_as_langchain(self):
        prompt = ChatPrompt(messages=[Message(type=ChatMessageEnum.HUMAN.value, content='Hi')])
        template = prompt.as_langchain()
        assert isinstance(template, ChatPromptTemplate)
        assert len(template.messages) == 1

    def test_extract_placeholders(self):
        prompt = ChatPrompt(messages=[
            Message(type=ChatMessageEnum.HUMAN.value, content='Hello {name}, do {task}')
        ])
        assert set(prompt.extract_placeholders()) == {'name', 'task'}

    def test_build_prompt_orders_messages(self):
        prompt = ChatPrompt()
        model = AgentPromptModel(introduction='Intro', instruction='Task')
        prompt.build_prompt(model, ['introduction', 'instruction'])
        assert len(prompt.messages) == 2
        assert prompt.messages[0].type == ChatMessageEnum.SYSTEM.value

    def test_generate_image_prompt_http_url(self):
        prompt = ChatPrompt()
        prompt.generate_image_prompt(['https://example.com/a.png'])
        assert len(prompt.messages) == 1
        content = prompt.messages[0].content
        assert content[0]['type'] == 'image_url'

    def test_generate_image_prompt_ignores_bad_extension(self, tmp_path):
        prompt = ChatPrompt()
        prompt.generate_image_prompt(['note.txt'])
        assert prompt.messages == []

    def test_generate_image_prompt_dict_url(self):
        prompt = ChatPrompt()
        prompt.generate_image_prompt([{'url': 'https://example.com/b.jpg'}])
        assert len(prompt.messages) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
