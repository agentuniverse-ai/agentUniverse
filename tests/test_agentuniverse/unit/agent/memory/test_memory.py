# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/20 17:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_memory.py
import unittest

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import PromptTemplate

from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.memory.enum import MemoryTypeEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM

template = """
You are a chatbot having a conversation with a human.

Previous conversation:
{chat_history}

Human: {human_input}
Chatbot:
"""


class MemoryTest(unittest.TestCase):
    """
    Test cases for Memory class
    """

    def setUp(self) -> None:
        """Build a ChatMemory instance backed by a DefaultOpenAILLM."""
        init_params = dict()
        init_params['model_name'] = 'gpt-4o'
        init_params['temperature'] = 0.7
        init_params['max_retries'] = 2
        init_params['streaming'] = False

        init_params['llm'] = DefaultOpenAILLM(**init_params)
        init_params['memory_key'] = 'chat_history'
        init_params['max_tokens'] = '1024'
        init_params['type'] = MemoryTypeEnum.LONG_TERM
        self.message0 = Message(type='system', content='This is the system message')
        self.message1 = Message(type='human', content='Hi, my name is Edwin')
        self.message2 = Message(type='ai', content='Hello Edwin, nice to meet you.')
        init_params['messages'] = [self.message0, self.message1, self.message2]
        self.chat_memory = ChatMemory(**init_params)

    def test_summarize_memory_1(self) -> None:
        """Verify long-term memory summarises history via ConversationChain."""
        langchain_memory = self.chat_memory.as_langchain()
        langchain_memory.memory_key = 'history'
        llm_chain = ConversationChain(llm=langchain_memory.llm,
                                      memory=langchain_memory)
        conversation = llm_chain.predict(input='Who am I？')
        print(conversation)

    def test_summarize_memory_2(self) -> None:
        """Verify long-term memory works through a prompt-templated LLMChain."""
        langchain_memory = self.chat_memory.as_langchain()
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], template=template
        )
        llm_chain = LLMChain(llm=langchain_memory.llm, prompt=prompt,
                             memory=langchain_memory)
        conversation = llm_chain.predict(human_input='Who am I？')
        print(conversation)

    def test_summarize_memory_3(self) -> None:
        """Verify long-term memory summary produced with a verbose chain."""
        langchain_memory = self.chat_memory.as_langchain()
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], template=template
        )
        llm_chain = LLMChain(llm=langchain_memory.llm, verbose=True,
                             memory=langchain_memory, prompt=prompt)
        res = llm_chain(inputs={'human_input': 'What is my name?'})
        print(res)

    def test_truncate_memory_1(self) -> None:
        """Verify short-term memory truncation drives a langchain conversation."""
        self.chat_memory.type = MemoryTypeEnum.SHORT_TERM
        langchain_memory = self.chat_memory.as_langchain()
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], template=template
        )
        llm_chain = LLMChain(llm=langchain_memory.llm, prompt=prompt,
                             memory=langchain_memory)
        conversation = llm_chain.predict(human_input='Who am I？')
        print(conversation)

    def test_truncate_memory_2(self) -> None:
        """Verify short-term memory truncation works with direct chain inputs."""
        self.chat_memory.type = MemoryTypeEnum.SHORT_TERM
        langchain_memory = self.chat_memory.as_langchain()
        prompt = PromptTemplate(
            input_variables=["chat_history", "human_input"], template=template
        )
        llm_chain = LLMChain(llm=langchain_memory.llm,
                             memory=langchain_memory, prompt=prompt)
        res = llm_chain({'human_input': 'What is my name?'})
        print(res)


if __name__ == '__main__':
    unittest.main()
