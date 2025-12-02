# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: supervision_agent_template.py
from queue import Queue

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger
from agentuniverse.base.util.common_util import stream_output
from agentuniverse.base.util.logging.logging_util import LOGGER


class SupervisionAgentTemplate(AgentTemplate):
    """Agent template for supervision in IS pattern.

    This agent monitors implementation progress and provides feedback
    to ensure alignment with user goals.
    """

    def input_keys(self) -> list[str]:
        """Define input keys required by this agent.

        Returns:
            list[str]: List of input keys
        """
        return ['input', 'checkpoint_index', 'implementation_result', 'execution_context']

    def output_keys(self) -> list[str]:
        """Define output keys produced by this agent.

        Returns:
            list[str]: List of output keys ['needs_correction', 'feedback', 'score']
        """
        return ['needs_correction', 'feedback', 'score']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Parse and prepare input for the supervision agent.

        Args:
            input_object (InputObject): The input object containing user data.
            agent_input (dict): The agent input dictionary to be updated.

        Returns:
            dict: Updated agent input dictionary.
        """
        agent_input['input'] = input_object.get_data('input')

        # Checkpoint information
        agent_input['checkpoint_index'] = input_object.get_data('checkpoint_index', 0)

        # Get implementation result
        implementation_result = input_object.get_data('implementation_result')
        if implementation_result:
            agent_input['implementation_output'] = implementation_result.get_data('checkpoint_output', '')
        else:
            agent_input['implementation_output'] = ''

        # Execution context
        execution_context = input_object.get_data('execution_context', {})
        agent_input['user_goal'] = execution_context.get('user_goal', '')
        agent_input['checkpoint_history'] = execution_context.get('checkpoint_history', [])
        agent_input['corrections_made'] = execution_context.get('corrections_made', 0)

        # Get expert framework guidance if available
        agent_input['expert_framework'] = input_object.get_data('expert_framework', {}).get('supervision', '')

        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        """Parse the agent execution result.

        Args:
            agent_result (dict): Raw result from agent execution.

        Returns:
            dict: Parsed result with supervision decision and feedback.
        """
        final_result = dict()
        output = agent_result.get('output', '')

        # Extract supervision decision
        # The output should contain structured information about:
        # 1. needs_correction (bool): Whether correction is needed
        # 2. feedback (str): Detailed feedback for correction
        # 3. score (int): Quality score (0-100)

        # Parse the output to extract structured fields
        needs_correction = self._extract_needs_correction(output)
        feedback = self._extract_feedback(output)
        score = self._extract_score(output)

        final_result['needs_correction'] = needs_correction
        final_result['feedback'] = feedback
        final_result['score'] = score
        final_result['output'] = output

        # Add supervision agent log info
        checkpoint_idx = agent_result.get('checkpoint_index', 0)
        logger_info = f"\nSupervision agent checkpoint {checkpoint_idx} result:\n"
        logger_info += f"Needs correction: {needs_correction}, Score: {score}\n"
        logger_info += f"Feedback: {feedback}\n"
        LOGGER.info(logger_info)

        return final_result

    def _extract_needs_correction(self, output: str) -> bool:
        """Extract needs_correction flag from output.

        Args:
            output (str): Agent output text.

        Returns:
            bool: Whether correction is needed.
        """
        # Look for explicit correction markers in the output
        output_lower = output.lower()

        # Positive indicators (needs correction)
        correction_needed_markers = [
            'needs correction',
            '需要修正',
            '需要改进',
            'correction required',
            'needs improvement',
            '不符合要求',
            'does not meet'
        ]

        # Negative indicators (no correction needed)
        no_correction_markers = [
            'no correction needed',
            '无需修正',
            '符合要求',
            'meets requirements',
            'satisfactory',
            'acceptable'
        ]

        # Check for explicit markers
        for marker in no_correction_markers:
            if marker in output_lower:
                return False

        for marker in correction_needed_markers:
            if marker in output_lower:
                return True

        # Default to no correction if not explicitly stated
        return False

    def _extract_feedback(self, output: str) -> str:
        """Extract feedback text from output.

        Args:
            output (str): Agent output text.

        Returns:
            str: Extracted feedback.
        """
        # Try to extract feedback section
        feedback_markers = [
            'feedback:',
            '反馈:',
            '建议:',
            'suggestion:',
            'recommendations:'
        ]

        for marker in feedback_markers:
            if marker in output.lower():
                parts = output.lower().split(marker, 1)
                if len(parts) > 1:
                    # Extract text after marker until next section or end
                    feedback_text = parts[1].split('\n\n')[0].strip()
                    return feedback_text

        # If no explicit feedback section, return the full output
        return output

    def _extract_score(self, output: str) -> int:
        """Extract quality score from output.

        Args:
            output (str): Agent output text.

        Returns:
            int: Quality score (0-100), default 50 if not found.
        """
        import re

        # Look for score patterns like "score: 85" or "评分: 85"
        score_patterns = [
            r'score[:\s]+(\d+)',
            r'评分[:\s]+(\d+)',
            r'得分[:\s]+(\d+)',
            r'quality[:\s]+(\d+)'
        ]

        for pattern in score_patterns:
            matches = re.findall(pattern, output.lower())
            if matches:
                try:
                    score = int(matches[0])
                    # Ensure score is in valid range
                    return max(0, min(100, score))
                except ValueError:
                    continue

        # Default score if not found
        return 50

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'SupervisionAgentTemplate':
        """Initialize the supervision agent template by component configer.

        Args:
            component_configer (AgentConfiger): The agent configuration object.

        Returns:
            SupervisionAgentTemplate: Initialized template instance.
        """
        super().initialize_by_component_configer(component_configer)
        self.prompt_version = self.agent_model.profile.get('prompt_version', 'default_supervision_agent.cn')
        self.validate_required_params()
        return self

    def validate_required_params(self):
        """Validate that required parameters are set.

        Raises:
            ValueError: If llm_name is not set.
        """
        if not self.llm_name:
            raise ValueError(f'llm_name of the agent {self.agent_model.info.get("name")}'
                           f' is not set, please go to the agent profile configuration'
                           ' and set the `name` attribute in the `llm_model`.')

    def add_output_stream(self, output_stream: Queue, agent_output: str) -> None:
        """Add output to the stream for real-time feedback.

        Args:
            output_stream (Queue): The output stream queue.
            agent_output (str): The agent output to stream.
        """
        if not output_stream:
            return
        # Add supervision agent final result into the stream output
        stream_output(output_stream,
                     {"data": {
                         'output': agent_output,
                         "agent_info": self.agent_model.info
                     }, "type": "supervision"})
