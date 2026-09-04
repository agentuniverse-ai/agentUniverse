# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 14:26
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: rag_agent_case_template.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class RagAgentCaseTemplate(RagAgentTemplate):
    """A RAG agent template that grounds answers with a web search and memory."""

    def execute_query(self, input: str):
        """
        Args:
            input: user query
        """
        # 1. do question analyze
        agent_instance: AgentTemplate = AgentManager().get_instance_obj('question_agent_case')
        output_object = agent_instance.run(input=input)
        output = output_object.get_data('output')
        query_info = parse_json_markdown(output)
        if not query_info.get('need_google_search'):
            return "no_question"
        # 2. do google search
        questions = query_info.get('search_questions')
        tool = ToolManager().get_instance_obj('google_search_tool')
        background = []
        for question in questions:
            background.append(tool.run(input=question))
        return "Google Search Result: \n" + "\n\n".join(background)

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        """Run the customized RAG flow: tool grounding, memory handling, and the LLM chain.

        Args:
            input_object: The input object carrying the output stream.
            agent_input: The agent input dict, updated with background and memory.
            memory: The memory used to store and summarize the conversation.
            llm: The LLM instance used to build the chain.
            prompt: The prompt template used to build the chain.

        Returns:
            The agent input dict enriched with the answer under 'output'.
        """
        # invoke tool
        knowledge_res: str = self.execute_query(agent_input.get('input'))
        agent_input['background'] = knowledge_res

        # 1. load memory
        self.load_memory(memory, agent_input)
        # 2. add user query memory
        self.add_memory(memory, f"{agent_input.get('input')}", type='human', agent_input=agent_input)
        # 3. load summarize memory
        summarize_memory = self.load_summarize_memory(memory, agent_input)
        agent_input['background'] = (agent_input['background']
                                     + f"\nsummarize_memory:\n {summarize_memory}")
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
        # 4. invoke chain
        chain = prompt.as_langchain() | llm.as_langchain_runnable(
            self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
        # 5. stream output
        self.add_output_stream(input_object.get_data('output_stream'), res)
        # 6. add answer memory
        self.add_memory(memory, f"{res}", agent_input=agent_input, type='ai')
        # 7. do memory summarize
        self.summarize_memory(agent_input, memory)
        return {**agent_input, 'output': res}
