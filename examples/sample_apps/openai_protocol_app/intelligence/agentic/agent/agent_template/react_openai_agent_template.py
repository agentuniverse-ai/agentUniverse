from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate
from agentuniverse.agent.template.react_agent_template import ReActAgentTemplate
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt import Prompt


class ReActOpenAIAgentTemplate(OpenAIProtocolTemplate, ReActAgentTemplate):
    """Agent template exposing the ReAct agent flow through the OpenAI protocol."""

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory, llm: LLM, prompt: Prompt,
                           **kwargs) -> dict:
        """Execute the ReAct-style agent chain and return the merged result dict.

        Args:
            input_object: The wrapped user request payload.
            agent_input: Mutable dict holding the agent's working inputs.
            memory: The memory component used for conversational history.
            llm: The LLM component driving the reasoning loop.
            prompt: The prompt component formatting each reasoning step.
            **kwargs: Extra kwargs forwarded to the parent template execution.

        Returns:
            dict: The output dict produced by ReActAgentTemplate.
        """
        return ReActAgentTemplate.customized_execute(self, input_object, agent_input, memory, llm, prompt, **kwargs)
