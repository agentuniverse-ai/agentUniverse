# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 21:11
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_service.py
from datetime import datetime
import json
import time
import os
from typing import List, Tuple, Iterator, AsyncIterator

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent_serve.web.request_task import RequestTask
from agentuniverse.agent_serve.web.web_util import agent_run_queue, async_agent_run_queue
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse_product.base.product_manager import Product
from agentuniverse_product.base.product_manager import ProductManager
from agentuniverse_product.base.util.yaml_util import write_yaml_file
from agentuniverse_product.service.message_service.message_service import MessageService
from agentuniverse_product.service.model.agent_dto import AgentDTO
from agentuniverse_product.service.model.message_dto import MessageDTO
from agentuniverse_product.service.model.session_dto import SessionDTO
from agentuniverse_product.service.session_service.session_service import SessionService
from agentuniverse_product.service.util.agent_util import validate_create_agent_parameters, \
    assemble_product_config_data, assemble_agent_config_data, assemble_agent_dto, update_agent_product_config, \
    update_agent_config, register_agent, register_product, validate_and_assemble_agent_input
from agentuniverse_product.service.util.common_util import get_core_path
from agentuniverse_product.service.util.monitor_util import monitor_context, get_monitor_data


class AgentService:
    """Agent Service for aU-product."""

    @staticmethod
    def get_agent_list() -> List[AgentDTO]:
        """Get all agents.

        Returns:
            List[AgentDTO]: List of AgentDTOs.
        """
        res = []
        product_list: List[Product] = ProductManager().get_instance_obj_list()
        if len(product_list) < 1:
            return res
        for product in product_list:
            if product.type == ComponentEnum.AGENT.value:
                agent_dto = AgentDTO(nickname=product.nickname, avatar=product.avatar, id=product.id,
                                     opening_speech=product.opening_speech, mtime=product.get_mtime())
                agent = product.instance
                agent_model: AgentModel = agent.agent_model
                agent_dto.description = agent_model.info.get('description', '')
                res.append(agent_dto)
        return res

    @staticmethod
    def get_agent_detail(id: str) -> AgentDTO | None:
        """Get agent detail by agent id.

        Returns:
            AgentDTO | None: AgentDTO or None.
        """
        product: Product = ProductManager().get_instance_obj(id, new_instance=False)
        agent: Agent = AgentManager().get_instance_obj(id, new_instance=False)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")
        agent_dto = AgentDTO(id=id,
                             nickname=product.nickname if product else '',
                             avatar=product.avatar if product else '',
                             opening_speech=product.opening_speech if product else '',
                             mtime=product.get_mtime())
        # assemble agent dto
        return assemble_agent_dto(agent, agent_dto)

    @staticmethod
    def update_agent(agent_dto: AgentDTO) -> None:
        """Update agent detail."""
        if agent_dto.id is None:
            raise ValueError("Agent id cannot be None.")
        product: Product = ProductManager().get_instance_obj(agent_dto.id)
        agent: Agent = AgentManager().get_instance_obj(agent_dto.id, new_instance=False)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")
        # update agent product yaml configuration file
        if product:
            update_agent_product_config(product, agent_dto, product.component_config_path)
        # update agent yaml configuration file
        update_agent_config(agent, agent_dto, agent.component_config_path)

    @staticmethod
    def chat(agent_id: str, session_id: str, input: str) -> dict:
        """Chat with agent and get response.

        Args:
            agent_id (str): Agent id.
            session_id (str): Session id.
            input (str): Query string.
        Returns:
            dict: Response.
        """
        if agent_id is None or session_id is None:
            raise ValueError("Agent id or session id cannot be None.")
        agent: Agent = AgentManager().get_instance_obj(agent_id, new_instance=False)
        if agent is None:
            raise ValueError("The agent instance corresponding to the agent id cannot be found.")

        # invoke agent with monitor context
        with monitor_context():
            start_time = time.time()
            output_object: OutputObject = agent.run(input=input, session_id=session_id)
            end_time = time.time()
            # calculate response time
            response_time = round((end_time - start_time) * 1000, 2)
            output = output_object.get_data('output')
            
            # get invocation chain and token usage
            invocation_chain, token_usage = get_monitor_data()

        # add agent chat history
        session_id, message_id = AgentService().add_agent_chat_history(agent_id, session_id, input, output,
                                                                       datetime.fromtimestamp(end_time))

        return {'response_time': response_time, 'message_id': message_id, 'session_id': session_id, 'output': output,
                'start_time': datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                'end_time': datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                'invocation_chain': invocation_chain, 'token_usage': token_usage}

    @staticmethod
    def stream_chat(agent_id: str, session_id: str, input: str) -> Iterator:
        """Stream chat with agent and get response.

        Args:
            agent_id (str): Agent id.
            session_id (str): Session id.
            input (str): Query string.
        Returns:
            Iterator: Response.
        """
        agent_input_dict = validate_and_assemble_agent_input(agent_id, session_id, input,
                                                             AgentService().get_agent_chat_history(session_id))

        # invoke agent with monitor context
        with monitor_context():
            # invoke agent
            start_time = time.time()
            task = RequestTask(agent_run_queue, False,
                               **agent_input_dict)

            # generate iterator
            for chunk in task.stream_run():
                chunk_dict = json.loads(chunk.replace("data:", "", 1))
                if "process" in chunk_dict:
                    data = chunk_dict['process'].get('data')
                    if data:
                        yield_type = 'token' if 'chunk' in data else 'intermediate_steps'
                        yield {'output': data.get('chunk' if yield_type == 'token' else 'output'),
                               'type': yield_type,
                               'agent_id': data.get('agent_info', {}).get('name', '')}
                elif "result" in chunk_dict or "error" in chunk_dict:
                    end_time = time.time()
                    # calculate response time
                    response_time = round((end_time - start_time) * 1000, 2)
                    if "result" in chunk_dict:
                        output = chunk_dict['result'].get('output')
                        # add agent chat history
                        session_id, message_id = AgentService().add_agent_chat_history(
                            agent_id, session_id, input, output, datetime.fromtimestamp(end_time)
                        )
                        # get contexts
                        invocation_chain, token_usage = get_monitor_data()
                        # return final yield
                        yield {
                            'response_time': response_time,
                            'message_id': message_id,
                            'session_id': session_id,
                            'output': output,
                            'start_time': datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                            'end_time': datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                            'invocation_chain': invocation_chain,
                            'token_usage': token_usage,
                            'type': 'final_result'
                        }
                    else:
                        yield {'error': chunk_dict['error'], 'type': 'error'}

    @staticmethod
    async def async_stream_chat(agent_id: str, session_id: str, input: str) -> AsyncIterator:
        """Asynchronously stream chat with agent and get response.

        Args:
            agent_id (str): Agent id.
            session_id (str): Session id.
            input (str): Query string.
        Returns:
            AsyncIterator: Response.
        """
        agent_input_dict = validate_and_assemble_agent_input(agent_id, session_id, input,
                                                             AgentService().get_agent_chat_history(session_id))

        # invoke agent with monitor context
        with monitor_context():
            # invoke agent
            start_time = time.time()
            task = RequestTask(async_agent_run_queue, False, **agent_input_dict)

            # generate async iterator
            async for chunk in task.async_stream_run():
                chunk_dict = json.loads(chunk.replace("data:", "", 1))
                if "process" in chunk_dict:
                    data = chunk_dict['process'].get('data')
                    if data:
                        yield_type = 'token' if 'chunk' in data else 'intermediate_steps'
                        output = data.get('chunk' if yield_type == 'token' else 'output')
                        if not isinstance(output, str) and isinstance(output, dict) and output.get('text'):
                            output = output.get('text')
                        yield {'output': output,
                               'type': yield_type,
                               'agent_id': data.get('agent_info', {}).get('name', '')}
                elif "result" in chunk_dict or "error" in chunk_dict:
                    end_time = time.time()
                    # calculate response time
                    response_time = round((end_time - start_time) * 1000, 2)
                    if "result" in chunk_dict:
                        output = chunk_dict['result'].get('output')
                        if not isinstance(output, str) and isinstance(output, dict) and output.get('text'):
                            output = output.get('text')
                        # add agent chat history
                        session_id, message_id = AgentService().add_agent_chat_history(
                            agent_id, session_id, input, output, datetime.fromtimestamp(end_time)
                        )
                        # get contexts
                        invocation_chain, token_usage = get_monitor_data()
                        # return final yield
                        yield {
                            'response_time': response_time,
                            'message_id': message_id,
                            'session_id': session_id,
                            'output': output,
                            'start_time': datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                            'end_time': datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                            'invocation_chain': invocation_chain,
                            'token_usage': token_usage,
                            'type': 'final_result'
                        }
                    else:
                        yield {'error': chunk_dict['error'], 'type': 'error'}

    @staticmethod
    def create_agent(agent_dto: AgentDTO) -> str:
        """Create an agent instance.

        Args:
            agent_dto (AgentDTO): AgentDTO.
        Returns:
            str: Agent id.
        """
        # validate parameters
        validate_create_agent_parameters(agent_dto)

        # assemble product config data
        product_config_data = assemble_product_config_data(agent_dto)

        # write product YAML file
        product_file_name = f"{agent_dto.id}_product"

        path = get_core_path()
        product_file_path = path / 'product' / 'agent' / f"{product_file_name}.yaml" if path \
            else os.path.join('..', '..', 'platform', 'difizen', 'product', 'agent', f"{product_file_name}.yaml")
        write_yaml_file(str(product_file_path), product_config_data)

        # assemble agent config data
        agent_config_data = assemble_agent_config_data(agent_dto)

        # write agent YAML file
        agent_file_path = path / 'agent' / f"{agent_dto.id}.yaml" if path \
            else os.path.join('..', '..', 'intelligence', 'agentic', 'agent', f"{agent_dto.id}.yaml")
        write_yaml_file(str(agent_file_path), agent_config_data)

        # register product and agent instance
        register_agent(str(agent_file_path))
        register_product(str(product_file_path))
        return agent_dto.id

    @staticmethod
    def get_agent_chat_history(session_id: str) -> list:
        """Get agent chat history from session db table by session id."""
        # newest top5
        session_dto: SessionDTO = SessionService().get_session_detail(session_id, 5)
        chat_history = []
        if session_dto:
            messages: List[MessageDTO] = session_dto.messages
            if len(messages) > 0:
                for message in messages:
                    content: str = message.content
                    if content is not None:
                        chat_history.extend(json.loads(content))
        return chat_history

    @staticmethod
    def add_agent_chat_history(agent_id: str, session_id: str,
                               input: str, output: str, cur_time: datetime) -> Tuple[str, int]:
        """Add agent chat history to session and message db tables."""
        content = json.dumps([{'type': 'human', 'content': input}, {'type': 'ai', 'content': output}],
                             ensure_ascii=False)
        session_id = SessionService.update_session(session_id, agent_id, cur_time)
        message_id = MessageService.add_message(session_id, content, cur_time)
        return session_id, message_id
