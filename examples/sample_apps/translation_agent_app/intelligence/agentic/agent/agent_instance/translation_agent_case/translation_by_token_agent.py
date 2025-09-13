# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/25 16:56
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_planner.py
from queue import Queue

from langchain_text_splitters import RecursiveCharacterTextSplitter
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


def calculate_chunk_size(token_count: int, token_limit: int) -> int:
    if token_count <= token_limit:
        return token_count

    num_chunks = (token_count + token_limit - 1) // token_limit
    chunk_size = token_count // num_chunks

    remaining_tokens = token_count % token_limit
    if remaining_tokens > 0:
        chunk_size += remaining_tokens // num_chunks

    return chunk_size


def output_middle_result(input_object: InputObject, data: any):
    output_stream: Queue = input_object.get_data('output_stream', None)
    if output_stream:
        output_stream.put(data)


class TranslationAgent(Agent):
    def input_keys(self) -> list[str]:
        return self.agent_model.profile.get('input_keys')

    def output_keys(self) -> list[str]:
        return self.agent_model.profile.get('output_keys')

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in input_object.to_dict():
            if key == 'output_stream':
                continue
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result

    def execute_agents(self, input_object: InputObject, planner_input: dict) -> dict:
        work_agent = 'translation_work_agent'
        reflection_agent = 'translation_reflection_agent'
        improve_agent = 'translation_improve_agent'

        init_agent_result = self.execute_agent(work_agent, planner_input)
        LOGGER.info(f"init_agent_result: {init_agent_result.to_json_str()}")
        output_middle_result(input_object, {'init_agent_result': init_agent_result.get_data('output')})

        planner_input['init_agent_result'] = init_agent_result.get_data('output')

        reflection_result = self.execute_agent(reflection_agent, planner_input)
        LOGGER.info(f"reflection_result: {reflection_result.to_json_str()}")
        output_middle_result(input_object, {'reflection_agent_result': reflection_result.get_data('output')})

        planner_input['reflection_agent_result'] = reflection_result.get_data('output')

        improve_result = self.execute_agent(improve_agent, planner_input)
        LOGGER.info(f"improve_agent_result: {improve_result.to_json_str()}")
        output_middle_result(input_object, {'improve_agent_result': improve_result.get_data('output')})

        return improve_result.to_dict()

    @staticmethod
    def execute_agent(agent_name: str, agent_input: dict):
        agent: Agent = AgentManager().get_instance_obj(agent_name)
        result = agent.run(**agent_input)
        return result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        llm_name = self.agent_model.profile.get('llm_model').get('name')
        llm: LLM = LLMManager().get_instance_obj(llm_name)
        source_text = agent_input.get('source_text')
        text_tokens = len(source_text)
        # 这里使用最大输入token，因为必须要保证有足够的token输出翻译结果
        if text_tokens < llm.max_tokens:
            return self.execute_agents(input_object, agent_input)
        agent_input['execute_type'] = 'multi'
        chunk_result = list[str]()
        chunk_size = calculate_chunk_size(text_tokens, llm.max_tokens)
        source_text_chunks = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0).split_text(
            source_text)

        for i in range(len(source_text_chunks)):
            tagged_text = (
                    "".join(source_text_chunks[0:i])
                    + "<TRANSLATE_THIS>"
                    + source_text_chunks[i]
                    + "</TRANSLATE_THIS>"
                    + "".join(source_text_chunks[i + 1:])
            )
            agent_input['chunk_to_translate'] = source_text_chunks[i]
            agent_input['tagged_text'] = tagged_text
            result = self.execute_agents(input_object, agent_input)
            chunk_result.append(result.get('output'))

        return {
            'output': "".join(chunk_result)
        }
