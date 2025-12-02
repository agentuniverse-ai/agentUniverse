# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: is_agent_template.py
from queue import Queue

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.workflow.work_pattern_manager import WorkPatternManager


class ISAgentTemplate(AgentTemplate):
    """Agent template for IS (Implementation-Supervision) pattern coordinator.

    This template coordinates implementation and supervision agents to ensure
    that task execution stays aligned with user goals through continuous monitoring.
    """

    # Sub-agent names
    implementation_agent_name: str = "ImplementationAgent"
    supervision_agent_name: str = "SupervisionAgent"

    # Default configuration
    checkpoint_count: int = 3
    max_corrections: int = 2

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ['input']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys
        """
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the IS agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input['input'] = input_object.get_data('input')

        # Get configuration parameters
        agent_input['checkpoint_count'] = input_object.get_data(
            'checkpoint_count',
            self.checkpoint_count
        )
        agent_input['max_corrections'] = input_object.get_data(
            'max_corrections',
            self.max_corrections
        )

        return agent_input

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute IS pattern workflow.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The agent result dictionary.
        """
        # Build expert framework if enabled
        self.agent_model.profile['expert_framework'] = self._build_expert_framework(
            agent_input,
            input_object
        )

        # Generate sub-agents
        agents = self._generate_agents()

        # Get IS work pattern instance
        is_work_pattern = WorkPatternManager().get_instance_obj('is_work_pattern')

        # Inject agents into work pattern
        is_work_pattern = is_work_pattern.set_by_agent_model(**agents)

        # Execute work pattern
        work_pattern_result = self.customized_execute(
            is_work_pattern,
            input_object,
            agent_input,
            **kwargs
        )

        return work_pattern_result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        """Execute IS pattern workflow asynchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The agent result dictionary.
        """
        # Build expert framework if enabled
        self.agent_model.profile['expert_framework'] = self._build_expert_framework(
            agent_input,
            input_object
        )

        # Generate sub-agents
        agents = self._generate_agents()

        # Get IS work pattern instance
        is_work_pattern = WorkPatternManager().get_instance_obj('is_work_pattern')

        # Inject agents into work pattern
        is_work_pattern = is_work_pattern.set_by_agent_model(**agents)

        # Execute work pattern asynchronously
        work_pattern_result = await self.async_customized_execute(
            is_work_pattern,
            input_object,
            agent_input,
            **kwargs
        )

        return work_pattern_result

    def _generate_agents(self) -> dict:
        """Generate implementation and supervision agent instances.

        Returns:
            dict: Dictionary containing agent instances.
        """
        agents = {}

        # Get implementation agent
        implementation_agent_name = self.agent_model.profile.get(
            'implementation',
            self.implementation_agent_name
        )
        implementation_agent: Agent = AgentManager().get_instance_obj(implementation_agent_name)
        if implementation_agent:
            agents['implementation'] = implementation_agent

        # Get supervision agent
        supervision_agent_name = self.agent_model.profile.get(
            'supervision',
            self.supervision_agent_name
        )
        supervision_agent: Agent = AgentManager().get_instance_obj(supervision_agent_name)
        if supervision_agent:
            agents['supervision'] = supervision_agent

        return agents

    def _build_expert_framework(self, agent_input: dict, input_object: InputObject) -> dict:
        """Build expert framework for domain-specific guidance.

        Args:
            agent_input (dict): The agent input dictionary.
            input_object (InputObject): The input object.

        Returns:
            dict: Expert framework configuration for both agents.
        """
        expert_framework = {}

        # Check if expert framework is enabled in profile
        expert_framework_enabled = self.agent_model.profile.get('expert_framework_enabled', False)

        if not expert_framework_enabled:
            return expert_framework

        # Get expert framework configuration from profile or input
        expert_config = self.agent_model.profile.get('expert_framework', {})
        input_expert = input_object.get_data('expert_framework', {})

        # Implementation agent expert framework
        implementation_expert = input_expert.get('implementation') or expert_config.get('implementation', '')
        if implementation_expert:
            expert_framework['implementation'] = implementation_expert

        # Supervision agent expert framework
        supervision_expert = input_expert.get('supervision') or expert_config.get('supervision', '')
        if supervision_expert:
            expert_framework['supervision'] = supervision_expert

        return expert_framework

    def parse_result(self, planner_result: dict) -> dict:
        """Parse the work pattern execution result.

        Args:
            planner_result (dict): Raw result from work pattern execution.

        Returns:
            dict: Parsed result with formatted output.
        """
        final_result = dict()

        # Extract result and execution context
        is_results = planner_result.get('result', [])
        execution_context = planner_result.get('execution_context', {})

        # Build comprehensive output
        output_lines = []
        output_lines.append("=== IS Pattern Execution Results ===\n")

        # Summary
        total_checkpoints = len(is_results)
        corrections_made = execution_context.get('corrections_made', 0)
        output_lines.append(f"Total Checkpoints: {total_checkpoints}")
        output_lines.append(f"Corrections Made: {corrections_made}\n")

        # Checkpoint details
        for idx, checkpoint_result in enumerate(is_results):
            output_lines.append(f"\n--- Checkpoint {idx + 1} ---")

            # Implementation result
            impl_result = checkpoint_result.get('implementation_result', {})
            impl_output = impl_result.get('checkpoint_output', '')
            output_lines.append(f"Implementation Output:\n{impl_output}")

            # Supervision result
            super_result = checkpoint_result.get('supervision_result', {})
            needs_correction = super_result.get('needs_correction', False)
            feedback = super_result.get('feedback', '')
            score = super_result.get('score', 0)

            output_lines.append(f"\nSupervision:")
            output_lines.append(f"  - Score: {score}")
            output_lines.append(f"  - Needs Correction: {needs_correction}")
            if feedback:
                output_lines.append(f"  - Feedback: {feedback}")

            # Correction result if any
            if 'correction_result' in checkpoint_result:
                corr_result = checkpoint_result.get('correction_result', {})
                corr_output = corr_result.get('checkpoint_output', '')
                output_lines.append(f"\nCorrection Output:\n{corr_output}")

        # Final result
        if is_results:
            last_checkpoint = is_results[-1]
            final_impl = last_checkpoint.get('implementation_result', {})
            final_output = final_impl.get('checkpoint_output', '')
            output_lines.append(f"\n\n=== Final Output ===\n{final_output}")
            final_result['output'] = final_output
        else:
            final_result['output'] = ""

        # Store full details
        final_result['full_output'] = '\n'.join(output_lines)
        final_result['checkpoint_results'] = is_results
        final_result['execution_context'] = execution_context

        return final_result

    def customized_execute(self, work_pattern, input_object: InputObject,
                          agent_input: dict, **kwargs) -> dict:
        """Execute work pattern with customized logic.

        Args:
            work_pattern: The IS work pattern instance.
            input_object (InputObject): The input parameters.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The execution result.
        """
        # Add memory to input object if available
        memory: Memory = self.agent_model.memory
        if memory:
            input_object.add_data('memory', memory)

        # Execute work pattern
        work_pattern_result = work_pattern.invoke(
            input_object=input_object,
            work_pattern_input=agent_input,
            **kwargs
        )

        # Add to memory if available
        if memory:
            self._add_to_memory(memory, agent_input, work_pattern_result)

        # Add stream output
        output_stream: Queue = kwargs.get('output_stream', None)
        if output_stream:
            parsed_result = self.parse_result(work_pattern_result)
            self.add_output_stream(output_stream, parsed_result.get('full_output', ''))

        return work_pattern_result

    async def async_customized_execute(self, work_pattern, input_object: InputObject,
                                      agent_input: dict, **kwargs) -> dict:
        """Execute work pattern asynchronously with customized logic.

        Args:
            work_pattern: The IS work pattern instance.
            input_object (InputObject): The input parameters.
            agent_input (dict): The agent input dictionary.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The execution result.
        """
        # Add memory to input object if available
        memory: Memory = self.agent_model.memory
        if memory:
            input_object.add_data('memory', memory)

        # Execute work pattern asynchronously
        work_pattern_result = await work_pattern.async_invoke(
            input_object=input_object,
            work_pattern_input=agent_input,
            **kwargs
        )

        # Add to memory if available
        if memory:
            self._add_to_memory(memory, agent_input, work_pattern_result)

        # Add stream output
        output_stream: Queue = kwargs.get('output_stream', None)
        if output_stream:
            parsed_result = self.parse_result(work_pattern_result)
            self.add_output_stream(output_stream, parsed_result.get('full_output', ''))

        return work_pattern_result

    def _add_to_memory(self, memory: Memory, agent_input: dict, work_pattern_result: dict):
        """Add execution results to memory.

        Args:
            memory (Memory): The memory instance.
            agent_input (dict): The agent input dictionary.
            work_pattern_result (dict): The work pattern execution result.
        """
        # Parse result for storage
        parsed_result = self.parse_result(work_pattern_result)

        # Create message objects for memory
        user_message = {
            'role': 'user',
            'content': agent_input.get('input', '')
        }

        assistant_message = {
            'role': 'assistant',
            'content': parsed_result.get('output', '')
        }

        # Add to memory
        memory.add_message(user_message)
        memory.add_message(assistant_message)

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'ISAgentTemplate':
        """Initialize the IS agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            ISAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)

        # Load configuration
        profile = self.agent_model.profile
        self.implementation_agent_name = profile.get('implementation', self.implementation_agent_name)
        self.supervision_agent_name = profile.get('supervision', self.supervision_agent_name)
        self.checkpoint_count = profile.get('checkpoint_count', self.checkpoint_count)
        self.max_corrections = profile.get('max_corrections', self.max_corrections)

        return self
