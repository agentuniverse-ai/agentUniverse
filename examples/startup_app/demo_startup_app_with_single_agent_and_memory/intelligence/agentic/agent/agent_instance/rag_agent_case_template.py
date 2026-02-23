# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 14:26
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: rag_agent_case_template.py

from agentuniverse.base.util.common_util import parse_json_markdown

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.ai_context.agent_context import AgentContext
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt


class RagAgentCaseTemplate(RagAgentTemplate):
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

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM,
                           agent_context: AgentContext = None, **kwargs) -> dict:
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
        # 4. invoke llm
        prompt: ChatPrompt = self.process_prompt(agent_input, **kwargs)
        messages = prompt.render(**agent_input)
        llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
        res = llm_output.text
        # 5. stream output
        self.add_output_stream(input_object.get_data('output_stream'), res)
        # 6. add answer memory
        self.add_memory(memory, f"{res}", agent_input=agent_input, type='ai')
        # 7. do memory summarize
        self.summarize_memory(agent_input, memory)
        return {**agent_input, 'output': res}
