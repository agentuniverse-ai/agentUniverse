from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.util.agent_util import assemble_memory_output, assemble_memory_input
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt


class CritiqueAgentTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        return ['input', 'draft']

    def output_keys(self) -> list[str]:
        return ['critique_result']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        user_input = input_object.get_data("input", "")
        draft = input_object.get_data("draft", "")
        agent_input["input"] = user_input
        agent_input["draft"] = draft

        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        final_result = dict()

        output = agent_result.get('critique_result')
        output = parse_json_markdown(output)

        critique = output.get('critique')
        suggestion = output.get('suggestion')
        score = output.get('score')

        final_result['critique_result'] = output
        final_result['score'] = score
        final_result['critique'] = critique
        final_result['suggestion'] = suggestion

        # add critique agent log info.
        logger_info = f"\nCritique agent execution result is :\n"
        critique_info_str = f"critique: {critique} \n"
        critique_info_str += f"suggestion: {suggestion} \n"
        critique_info_str += f"score: {score} \n"
        LOGGER.info(logger_info + critique_info_str)

        return final_result

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """
        执行生成任务

        Args:
            input_object: 输入对象
            agent_input: 智能体输入字典

        Returns:
            生成结果字典
        """
        memory: Memory = self.process_memory(agent_input, **kwargs)

        self.run_all_actions(self.agent_model, agent_input, input_object)

        llm: LLM = self.get_llm(self.agent_model)

        prompt: Prompt = self.process_prompt(agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)

        assemble_memory_input(memory, agent_input)

        chain = prompt.as_langchain() | llm.as_langchain_runnable(self.agent_model.llm_params()) | StrOutputParser()
        res = chain.invoke(input=agent_input)
        res = {'critique_result': res}

        assemble_memory_output(memory=memory,
                               agent_input=agent_input,
                               content=f"Human: {agent_input.get('input')}, AI: {res}")
        return {**agent_input, **res}

    def run_all_actions(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject):
        """Tool and knowledge processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        """
        action: dict = agent_model.action or dict()
        tools: list = action.get('tool') or list()
        knowledge: list = action.get('knowledge') or list()
        agents: list = action.get('agent') or list()

        action_result: list = list()

        for tool_name in tools:
            tool = ToolManager().get_instance_obj(tool_name)
            if tool is None:
                continue
            tool_input = {key: input_object.get_data(key) for key in tool.input_keys}
            action_result.append(tool.run(**tool_input))

        for knowledge_name in knowledge:
            knowledge: Knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
            if knowledge is None:
                continue
            knowledge_res: List[Document] = knowledge.query_knowledge(
                query_str=input_object.get_data(self.input_key),
                **input_object.to_dict()
            )
            action_result.append(knowledge.to_llm(knowledge_res))

        for agent_name in agents:
            agent = AgentManager().get_instance_obj(agent_name)
            if agent is None:
                continue
            agent_input = {key: input_object.get_data(key) for key in agent.input_keys()}
            output_object = agent.run(**agent_input)
            action_result.append("\n".join([output_object.get_data(key)
                                            for key in agent.output_keys()
                                            if output_object.get_data(key) is not None]))

        planner_input['background'] = planner_input['background'] or '' + "\n".join(action_result)


    def get_llm(self, agent_model: AgentModel) -> LLM:
        """Language model module processing.

        Args:
            agent_model (AgentModel): Agent model object.
        Returns:
            LLM: The language model.
        """
        llm_name = agent_model.profile.get('llm_model').get('name')
        llm: LLM = LLMManager().get_instance_obj(component_instance_name=llm_name)
        return llm