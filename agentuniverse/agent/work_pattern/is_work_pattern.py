# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : Claude Code
# @FileName: is_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.implementation_agent_template import ImplementationAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import SupervisionAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class ISWorkPattern(WorkPattern):
    """Implementation-Supervision work pattern for goal-aligned execution.

    This pattern uses two agents with distinct responsibilities:
    - Implementation: Executes the main process and tasks
    - Supervision: Monitors execution and provides feedback to ensure alignment with user goals

    The pattern ensures that execution stays aligned with user objectives through
    continuous supervision and feedback.
    """

    implementation: ImplementationAgentTemplate = None
    supervision: SupervisionAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute IS pattern synchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - checkpoint_count (int): Number of supervision checkpoints (default: 3)
                - max_corrections (int): Maximum number of corrections allowed (default: 2)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all checkpoint results.
        """
        self._validate_work_pattern_members()

        is_results = list()
        checkpoint_count = work_pattern_input.get('checkpoint_count', 3)
        max_corrections = work_pattern_input.get('max_corrections', 2)

        # Track overall execution state
        execution_context = {
            'user_goal': work_pattern_input.get('input'),
            'corrections_made': 0,
            'checkpoint_history': []
        }

        for checkpoint_idx in range(checkpoint_count):
            checkpoint_result = {}

            # Implementation agent executes a portion of the task
            implementation_result = self._invoke_implementation(
                input_object,
                work_pattern_input,
                checkpoint_idx,
                checkpoint_count,
                execution_context,
                checkpoint_result
            )

            # Supervision agent monitors and provides feedback
            supervision_result = self._invoke_supervision(
                input_object,
                checkpoint_idx,
                execution_context,
                checkpoint_result
            )

            # Check if correction is needed
            needs_correction = supervision_result.get('needs_correction', False)

            if needs_correction and execution_context['corrections_made'] < max_corrections:
                # Execute correction
                correction_result = self._invoke_correction(
                    input_object,
                    supervision_result,
                    checkpoint_result
                )
                execution_context['corrections_made'] += 1

            # Store checkpoint history
            execution_context['checkpoint_history'].append({
                'checkpoint': checkpoint_idx,
                'implementation': implementation_result,
                'supervision': supervision_result,
                'corrected': needs_correction
            })

            is_results.append(checkpoint_result)

        return {'result': is_results, 'execution_context': execution_context}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute IS pattern asynchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - checkpoint_count (int): Number of supervision checkpoints (default: 3)
                - max_corrections (int): Maximum number of corrections allowed (default: 2)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all checkpoint results.
        """
        self._validate_work_pattern_members()

        is_results = list()
        checkpoint_count = work_pattern_input.get('checkpoint_count', 3)
        max_corrections = work_pattern_input.get('max_corrections', 2)

        # Track overall execution state
        execution_context = {
            'user_goal': work_pattern_input.get('input'),
            'corrections_made': 0,
            'checkpoint_history': []
        }

        for checkpoint_idx in range(checkpoint_count):
            checkpoint_result = {}

            # Implementation agent executes a portion of the task
            implementation_result = await self._async_invoke_implementation(
                input_object,
                work_pattern_input,
                checkpoint_idx,
                checkpoint_count,
                execution_context,
                checkpoint_result
            )

            # Supervision agent monitors and provides feedback
            supervision_result = await self._async_invoke_supervision(
                input_object,
                checkpoint_idx,
                execution_context,
                checkpoint_result
            )

            # Check if correction is needed
            needs_correction = supervision_result.get('needs_correction', False)

            if needs_correction and execution_context['corrections_made'] < max_corrections:
                # Execute correction
                correction_result = await self._async_invoke_correction(
                    input_object,
                    supervision_result,
                    checkpoint_result
                )
                execution_context['corrections_made'] += 1

            # Store checkpoint history
            execution_context['checkpoint_history'].append({
                'checkpoint': checkpoint_idx,
                'implementation': implementation_result,
                'supervision': supervision_result,
                'corrected': needs_correction
            })

            is_results.append(checkpoint_result)

        return {'result': is_results, 'execution_context': execution_context}

    def _invoke_implementation(self, input_object: InputObject, agent_input: dict,
                              checkpoint_idx: int, checkpoint_count: int,
                              execution_context: dict, checkpoint_result: dict) -> dict:
        """Invoke implementation agent synchronously."""
        if not self.implementation:
            implementation_result = OutputObject({"output": agent_input.get('input')})
        else:
            # Add checkpoint information to input
            checkpoint_input = {
                **input_object.to_dict(),
                'checkpoint_index': checkpoint_idx,
                'total_checkpoints': checkpoint_count,
                'execution_context': execution_context
            }
            implementation_result = self.implementation.run(**checkpoint_input)
            checkpoint_result['implementation_result'] = implementation_result.to_dict()
        input_object.add_data('implementation_result', implementation_result)
        return implementation_result.to_dict()

    async def _async_invoke_implementation(self, input_object: InputObject, agent_input: dict,
                                          checkpoint_idx: int, checkpoint_count: int,
                                          execution_context: dict, checkpoint_result: dict) -> dict:
        """Invoke implementation agent asynchronously."""
        if not self.implementation:
            implementation_result = OutputObject({"output": agent_input.get('input')})
        else:
            # Add checkpoint information to input
            checkpoint_input = {
                **input_object.to_dict(),
                'checkpoint_index': checkpoint_idx,
                'total_checkpoints': checkpoint_count,
                'execution_context': execution_context
            }
            implementation_result = await self.implementation.async_run(**checkpoint_input)
            checkpoint_result['implementation_result'] = implementation_result.to_dict()
        input_object.add_data('implementation_result', implementation_result)
        return implementation_result.to_dict()

    def _invoke_supervision(self, input_object: InputObject, checkpoint_idx: int,
                           execution_context: dict, checkpoint_result: dict) -> dict:
        """Invoke supervision agent synchronously."""
        if not self.supervision:
            supervision_result = OutputObject({"needs_correction": False, "feedback": ""})
        else:
            supervision_input = {
                **input_object.to_dict(),
                'checkpoint_index': checkpoint_idx,
                'execution_context': execution_context
            }
            supervision_result = self.supervision.run(**supervision_input)
            checkpoint_result['supervision_result'] = supervision_result.to_dict()
        input_object.add_data('supervision_result', supervision_result)
        return supervision_result.to_dict()

    async def _async_invoke_supervision(self, input_object: InputObject, checkpoint_idx: int,
                                       execution_context: dict, checkpoint_result: dict) -> dict:
        """Invoke supervision agent asynchronously."""
        if not self.supervision:
            supervision_result = OutputObject({"needs_correction": False, "feedback": ""})
        else:
            supervision_input = {
                **input_object.to_dict(),
                'checkpoint_index': checkpoint_idx,
                'execution_context': execution_context
            }
            supervision_result = await self.supervision.async_run(**supervision_input)
            checkpoint_result['supervision_result'] = supervision_result.to_dict()
        input_object.add_data('supervision_result', supervision_result)
        return supervision_result.to_dict()

    def _invoke_correction(self, input_object: InputObject, supervision_result: dict,
                          checkpoint_result: dict) -> dict:
        """Invoke implementation agent for correction based on supervision feedback."""
        if not self.implementation:
            correction_result = OutputObject({})
        else:
            correction_input = {
                **input_object.to_dict(),
                'correction_mode': True,
                'supervision_feedback': supervision_result.get('feedback', '')
            }
            correction_result = self.implementation.run(**correction_input)
            checkpoint_result['correction_result'] = correction_result.to_dict()
        return correction_result.to_dict()

    async def _async_invoke_correction(self, input_object: InputObject, supervision_result: dict,
                                       checkpoint_result: dict) -> dict:
        """Invoke implementation agent for correction asynchronously."""
        if not self.implementation:
            correction_result = OutputObject({})
        else:
            correction_input = {
                **input_object.to_dict(),
                'correction_mode': True,
                'supervision_feedback': supervision_result.get('feedback', '')
            }
            correction_result = await self.implementation.async_run(**correction_input)
            checkpoint_result['correction_result'] = correction_result.to_dict()
        return correction_result.to_dict()

    def _validate_work_pattern_members(self):
        """Validate that agents are of the correct type."""
        if self.implementation and not isinstance(self.implementation, ImplementationAgentTemplate):
            raise ValueError(f"{self.implementation} is not of expected type ImplementationAgentTemplate.")
        if self.supervision and not isinstance(self.supervision, SupervisionAgentTemplate):
            raise ValueError(f"{self.supervision} is not of expected type SupervisionAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        """Create new instance with dynamically injected agents.

        Args:
            **kwargs: Agent instances to inject (implementation, supervision).

        Returns:
            ISWorkPattern: New instance with injected agents.
        """
        is_work_pattern_instance = self.__class__()
        is_work_pattern_instance.name = self.name
        is_work_pattern_instance.description = self.description
        for key in ['implementation', 'supervision']:
            if key in kwargs:
                setattr(is_work_pattern_instance, key, kwargs[key])
        return is_work_pattern_instance
