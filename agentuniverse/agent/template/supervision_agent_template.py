# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : kaichuan
# @FileName: supervision_agent_template.py
import re
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

    # The supervision prompt mandates a "Needs Correction: true/false" answer
    # line; accept the underscore form and surrounding markdown emphasis too.
    _EXPLICIT_VERDICT_PATTERN = re.compile(
        r'needs[\s_]*correction\s*[:：]\s*(?:[*_`]+\s*)*(true|false)(?![A-Za-z_])',
        re.IGNORECASE,
    )

    # Free-form fallback for model replies that omit the verdict line. Within
    # each alternative the longer, negated phrasings come first so that
    # "not acceptable" is not read as "acceptable" and "no correction
    # required" is not read as "correction required". The label form
    # "Needs Correction:" is excluded here because it is the answer field,
    # not prose, and is handled by the pattern above.
    _VERDICT_MARKER_PATTERN = re.compile(
        r'(?P<no_correction>'
        r'no correction needed|no correction required|无需修正|不需要修正'
        r'|meets requirements|satisfactory|acceptable|符合要求'
        r')'
        r'|(?P<correction>'
        r'needs[\s_]*correction(?!\s*[:：])|correction required(?!\s*[:：])'
        r'|needs improvement|需要修正|需要改进'
        r'|not acceptable|not satisfactory|does not meet|不符合要求'
        r')',
        re.IGNORECASE,
    )

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

        The supervision prompt asks the model to answer with an explicit
        ``Needs Correction: true/false`` line, so that line is the verdict and
        is honoured before any keyword heuristics run. Only when the model
        omits the line do we fall back to scanning the free-form text, where
        negated markers ("not acceptable", "不符合要求") must be recognised
        before their positive substrings ("acceptable", "符合要求").

        Args:
            output (str): Agent output text.

        Returns:
            bool: Whether correction is needed.
        """
        if not isinstance(output, str) or not output:
            return False

        explicit_verdict = self._EXPLICIT_VERDICT_PATTERN.search(output)
        if explicit_verdict:
            return explicit_verdict.group(1).lower() == 'true'

        # No explicit verdict: fall back to the first marker that appears in
        # the text. Matching left to right keeps "not acceptable" ahead of the
        # bare "acceptable" that sits inside it.
        for match in self._VERDICT_MARKER_PATTERN.finditer(output):
            return match.lastgroup == 'correction'

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

        import re

        for marker in feedback_markers:
            match = re.search(re.escape(marker), output, flags=re.IGNORECASE)
            if match:
                # Extract from the original output to preserve user-facing casing.
                return output[match.end():].split('\n\n', 1)[0].strip()

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
