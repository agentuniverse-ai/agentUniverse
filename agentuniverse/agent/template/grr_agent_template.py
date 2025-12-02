# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: grr_agent_template.py
from typing import Optional, Union

from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.generating_agent_template import GeneratingAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GRRWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class GRRAgentTemplate(AgentTemplate):
    """Coordinator template for GRR (Generate-Review-Rewrite) work pattern.

    This template coordinates three agents:
    - Generating Agent: Creates initial content
    - Reviewing Agent: Evaluates and provides feedback
    - Rewriting Agent: Improves content based on feedback

    The pattern iteratively refines content until quality threshold is met.
    """

    generating_agent_name: str = "GeneratingAgent"
    reviewing_agent_name: str = "ReviewingAgent"
    rewriting_agent_name: str = "RewritingAgent"
    eval_threshold: int = 60
    retry_count: int = 2
    expert_framework: Optional[dict[str, Union[str, dict]]] = None

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys ['input']
        """
        return ['input']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['output']
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the GRR pattern.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary with retry_count and eval_threshold.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({
            'eval_threshold': self.eval_threshold,
            'retry_count': self.retry_count
        })
        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute the GRR work pattern synchronously.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result.
        """
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GRRWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(
            input_object=input_object,
            agent_input=agent_input,
            memory=memory,
            grr_work_pattern=grr_work_pattern
        )
        self.add_grr_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute the GRR work pattern asynchronously.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result.
        """
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GRRWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = await self.customized_async_execute(
            input_object=input_object,
            agent_input=agent_input,
            memory=memory,
            grr_work_pattern=grr_work_pattern
        )
        self.add_grr_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def customized_execute(self, input_object: InputObject, agent_input: dict,
                          memory: Memory, grr_work_pattern: GRRWorkPattern, **kwargs) -> dict:
        """Customized execution logic for GRR pattern.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary.
            memory (Memory): The memory object.
            grr_work_pattern (GRRWorkPattern): The GRR work pattern instance.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result.
        """
        self.build_expert_framework(input_object)
        work_pattern_result = grr_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict,
                                      memory: Memory, grr_work_pattern: GRRWorkPattern, **kwargs) -> dict:
        """Customized asynchronous execution logic for GRR pattern.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary.
            memory (Memory): The memory object.
            grr_work_pattern (GRRWorkPattern): The GRR work pattern instance.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result.
        """
        self.build_expert_framework(input_object)
        work_pattern_result = await grr_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the work pattern result and extract final output.

        Args:
            agent_result (dict): Raw result from work pattern execution.

        Returns:
            dict: Parsed result with output key.
        """
        grr_results: list[dict] = agent_result.get('result', [])
        # Get the last successful result
        for item in reversed(grr_results):
            # Check if we have a rewritten result (preferred)
            rewriting_result = item.get('rewriting_result')
            if rewriting_result and rewriting_result.get('output'):
                return {'output': rewriting_result.get('output')}
            # Otherwise, use generating result
            generating_result = item.get('generating_result')
            if generating_result and generating_result.get('output'):
                return {'output': generating_result.get('output')}
        # Fallback to empty output
        return {'output': ''}

    def _generate_agents(self) -> dict:
        """Generate and validate agent instances.

        Returns:
            dict: Dictionary of agent instances.
        """
        generating_agent = self._get_and_validate_agent(self.generating_agent_name, GeneratingAgentTemplate)
        reviewing_agent = self._get_and_validate_agent(self.reviewing_agent_name, ReviewingAgentTemplate)
        rewriting_agent = self._get_and_validate_agent(self.rewriting_agent_name, RewritingAgentTemplate)
        return {
            'generating': generating_agent,
            'reviewing': reviewing_agent,
            'rewriting': rewriting_agent
        }

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        """Get agent instance and validate its type.

        Args:
            agent_name (str): Name of the agent to retrieve.
            expected_type (type): Expected type of the agent.

        Returns:
            Agent instance or None if not found.

        Raises:
            ValueError: If agent is not of expected type.
        """
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def add_grr_memory(self, grr_memory: Memory, agent_input: dict, work_pattern_result: dict):
        """Add GRR work pattern execution results to memory.

        Args:
            grr_memory (Memory): The memory object to update.
            agent_input (dict): The agent input dictionary.
            work_pattern_result (dict): The work pattern execution result.
        """
        if not grr_memory:
            return
        query = agent_input.get('input')
        message_list = []

        def _create_message_content(turn, role, agent_name, result):
            """Create memory message content for a specific turn and role."""
            content = (f"GRR work pattern turn {turn + 1}: The agent responsible for {role} is: {agent_name}, "
                      f"Human: {query}, AI: {result}")
            return Message(source=agent_name, content=content)

        for i, single_turn_res in enumerate(work_pattern_result.get('result', [])):
            generating_result = single_turn_res.get('generating_result', {})
            if generating_result:
                message_list.append(_create_message_content(
                    i, "generating content",
                    self.generating_agent_name,
                    generating_result.get('output')
                ))

            reviewing_result = single_turn_res.get('reviewing_result', {})
            if reviewing_result:
                review_info = f"Score: {reviewing_result.get('score')}, Suggestion: {reviewing_result.get('suggestion')}"
                message_list.append(_create_message_content(
                    i, "reviewing and evaluating content",
                    self.reviewing_agent_name,
                    review_info
                ))

            rewriting_result = single_turn_res.get('rewriting_result', {})
            if rewriting_result:
                message_list.append(_create_message_content(
                    i, "rewriting and improving content",
                    self.rewriting_agent_name,
                    rewriting_result.get('output')
                ))

        grr_memory.add(message_list, **agent_input)

    def build_expert_framework(self, input_object: InputObject):
        """Build expert framework from the expert framework tool selector or raw dictionary context.

        Args:
            input_object (InputObject): The input parameters passed by the user.

        Notes:
            The expert framework, whether using context or tool selector, must return a dictionary
            with keys for the specific content of generating, reviewing, and rewriting.
        """
        if self.expert_framework:
            context = self.expert_framework.get('context')
            selector = self.expert_framework.get('selector')

            # Tool selector must return a dictionary with keys for generating, reviewing, and rewriting
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                if not isinstance(selector_result, dict):
                    raise ValueError("The expert framework tool selector must return a dictionary with keys"
                                   " for the specific content of generating, reviewing, and rewriting.")
                input_object.add_data('expert_framework', selector_result)
            elif context:  # Raw dictionary context
                if not isinstance(context, dict):
                    raise ValueError("The expert framework raw context must be a dictionary with keys"
                                   " for the specific content of generating, reviewing, and rewriting.")
                input_object.add_data('expert_framework', context)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'GRRAgentTemplate':
        """Initialize the GRR agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            GRRAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        planner_config = self.agent_model.plan.get('planner', {})

        # Initialize agent names
        if self.agent_model.profile.get('generating') is not None or planner_config.get('generating') is not None:
            self.generating_agent_name = self.agent_model.profile.get('generating') \
                if self.agent_model.profile.get('generating') is not None else planner_config.get('generating')
        if self.agent_model.profile.get('reviewing') is not None or planner_config.get('reviewing') is not None:
            self.reviewing_agent_name = self.agent_model.profile.get('reviewing') \
                if self.agent_model.profile.get('reviewing') is not None else planner_config.get('reviewing')
        if self.agent_model.profile.get('rewriting') is not None or planner_config.get('rewriting') is not None:
            self.rewriting_agent_name = self.agent_model.profile.get('rewriting') \
                if self.agent_model.profile.get('rewriting') is not None else planner_config.get('rewriting')

        # Initialize configuration parameters
        if self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold'):
            self.eval_threshold = self.agent_model.profile.get('eval_threshold') or planner_config.get('eval_threshold')
        if self.agent_model.profile.get('retry_count') or planner_config.get('retry_count'):
            self.retry_count = self.agent_model.profile.get('retry_count') or planner_config.get('retry_count')
        if self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework'):
            self.expert_framework = \
                self.agent_model.profile.get('expert_framework') or planner_config.get('expert_framework')

        self.memory_name = self.agent_model.memory.get('name')
        return self
