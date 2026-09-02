# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:30
# @Author  : yuewang
# @FileName: test_chat_prompt.py
"""Unit tests for ChatPrompt."""

import pytest
from langchain_core.prompts import ChatPromptTemplate

from agentuniverse.agent.memory.message import Message
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt_model import AgentPromptModel


@pytest.fixture
def prompt():
    """Create an empty ChatPrompt."""
    return ChatPrompt()


class TestChatPromptBuild:
    """Test prompt building and placeholder extraction."""

    def test_as_langchain(self, prompt):
        prompt.messages = [Message(type='human', content='hi {q}')]
        lc = prompt.as_langchain()
        assert isinstance(lc, ChatPromptTemplate)

    def test_build_prompt_merges_system_messages(self, prompt):
        model = AgentPromptModel(introduction='intro', target='target', instruction='do it')
        result = prompt.build_prompt(model, ['introduction', 'target', 'instruction'])
        assert result is prompt
        assert prompt.messages[0].type == 'system'
        assert prompt.messages[0].content == 'intro\ntarget'
        assert prompt.messages[1].type == 'human'
        assert prompt.messages[1].content == 'do it'

    def test_extract_placeholders(self, prompt):
        prompt.messages = [
            Message(type='system', content='You are {role}'),
            Message(type='human', content='Answer {q} and {extra}'),
        ]
        assert prompt.extract_placeholders() == ['role', 'q', 'extra']


class TestChatPromptMedia:
    """Test image/audio prompt generation."""

    def test_generate_image_prompt_http_url(self, prompt):
        prompt.generate_image_prompt(['https://x.com/a.png'])
        assert len(prompt.messages) == 1
        assert prompt.messages[0].content[0] == {'type': 'image_url',
                                                 'image_url': {'url': 'https://x.com/a.png'}}

    def test_generate_image_prompt_dict_url(self, prompt):
        prompt.generate_image_prompt([{'url': 'https://x.com/b.png'}])
        assert prompt.messages[0].content[0]['image_url'] == {'url': 'https://x.com/b.png'}

    def test_generate_image_prompt_local_file(self, prompt, tmp_path):
        img = tmp_path / 'pic.png'
        img.write_bytes(b'\x89PNG')
        prompt.generate_image_prompt([str(img)])
        url = prompt.messages[0].content[0]['image_url']['url']
        assert url.startswith('data:image/png;base64,')

    def test_generate_image_prompt_ignores_non_image(self, prompt, tmp_path):
        txt = tmp_path / 'notes.txt'
        txt.write_bytes(b'hello')
        prompt.generate_image_prompt([str(txt)])
        assert prompt.messages == []

    def test_generate_audio_prompt(self, prompt):
        prompt.generate_audio_prompt('https://x.com/a.mp3')
        assert prompt.messages[0].content[0] == {'type': 'input_audio',
                                                 'input_audio': {'data': 'https://x.com/a.mp3'}}
        prompt.generate_audio_prompt(None)
        assert len(prompt.messages) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
