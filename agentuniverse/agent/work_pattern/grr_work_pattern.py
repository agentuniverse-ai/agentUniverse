# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/01
# @Author  : kaichuan
# @FileName: grr_work_pattern.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.template.generating_agent_template import GeneratingAgentTemplate
from agentuniverse.agent.template.reviewing_agent_template import ReviewingAgentTemplate
from agentuniverse.agent.template.rewriting_agent_template import RewritingAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class GRRWorkPattern(WorkPattern):
    """Generate-Review-Rewrite work pattern for content generation tasks.

    This pattern uses three agents with distinct responsibilities:
    - Generate: Creates initial content based on user specifications
    - Review: Reflects on and evaluates the generated content
    - Rewrite: Makes corrections and improvements based on review feedback

    The pattern iteratively refines content until quality threshold is met.
    """

    generating: GeneratingAgentTemplate = None
    reviewing: ReviewingAgentTemplate = None
    rewriting: RewritingAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute GRR pattern synchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - retry_count (int): Maximum number of refinement iterations (default: 2)
                - eval_threshold (int): Quality score threshold (default: 60)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all iteration results.
        """
        self._validate_work_pattern_members()

        grr_results = list()
        generating_result = dict()
        reviewing_result = dict()
        rewriting_result = dict()

        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        for iteration in range(retry_count):
            grr_round_results = {}

            # Generate content (first iteration) or use rewritten content
            if iteration == 0 or not rewriting_result:
                generating_result = self._invoke_generating(input_object, work_pattern_input, grr_round_results)
            else:
                # Use rewritten content as the new generated content
                generating_result = rewriting_result
                # Update input_object with rewritten content as generating and expressing result
                input_object.add_data('generating_result', OutputObject(generating_result))
                input_object.add_data('expressing_result', OutputObject(generating_result))

            # Review generated content
            reviewing_result = self._invoke_reviewing(input_object, grr_round_results)

            # Check if quality threshold met
            if reviewing_result.get('score') and reviewing_result.get('score') >= eval_threshold:
                grr_results.append(grr_round_results)
                break

            # Rewrite based on feedback if not meeting threshold
            if iteration < retry_count - 1:  # Don't rewrite on last iteration
                rewriting_result = self._invoke_rewriting(input_object, grr_round_results)

            grr_results.append(grr_round_results)

        return {'result': grr_results}

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        """Execute GRR pattern asynchronously.

        Args:
            input_object (InputObject): The input parameters passed by the user.
            work_pattern_input (dict): Work pattern input dictionary containing:
                - retry_count (int): Maximum number of refinement iterations (default: 2)
                - eval_threshold (int): Quality score threshold (default: 60)
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The work pattern result containing all iteration results.
        """
        self._validate_work_pattern_members()

        grr_results = list()
        generating_result = dict()
        reviewing_result = dict()
        rewriting_result = dict()

        retry_count = work_pattern_input.get('retry_count', 2)
        eval_threshold = work_pattern_input.get('eval_threshold', 60)

        for iteration in range(retry_count):
            grr_round_results = {}

            # Generate content (first iteration) or use rewritten content
            if iteration == 0 or not rewriting_result:
                generating_result = await self._async_invoke_generating(input_object, work_pattern_input,
                                                                        grr_round_results)
            else:
                # Use rewritten content as the new generated content
                generating_result = rewriting_result
                # Update input_object with rewritten content as generating and expressing result
                input_object.add_data('generating_result', OutputObject(generating_result))
                input_object.add_data('expressing_result', OutputObject(generating_result))

            # Review generated content
            reviewing_result = await self._async_invoke_reviewing(input_object, grr_round_results)

            # Check if quality threshold met
            if reviewing_result.get('score') and reviewing_result.get('score') >= eval_threshold:
                grr_results.append(grr_round_results)
                break

            # Rewrite based on feedback if not meeting threshold
            if iteration < retry_count - 1:  # Don't rewrite on last iteration
                rewriting_result = await self._async_invoke_rewriting(input_object, grr_round_results)

            grr_results.append(grr_round_results)

        return {'result': grr_results}

    def _invoke_generating(self, input_object: InputObject, agent_input: dict,
                          grr_round_results: dict) -> dict:
        """Invoke generating agent synchronously."""
        if not self.generating:
            generating_result = OutputObject({"output": agent_input.get('input')})
        else:
            generating_result = self.generating.run(**input_object.to_dict())
            grr_round_results['generating_result'] = generating_result.to_dict()
        input_object.add_data('generating_result', generating_result)
        # Also add as expressing_result for compatibility with ReviewingAgentTemplate
        input_object.add_data('expressing_result', generating_result)
        return generating_result.to_dict()

    async def _async_invoke_generating(self, input_object: InputObject, agent_input: dict,
                                       grr_round_results: dict) -> dict:
        """Invoke generating agent asynchronously."""
        if not self.generating:
            generating_result = OutputObject({"output": agent_input.get('input')})
        else:
            generating_result = await self.generating.async_run(**input_object.to_dict())
            grr_round_results['generating_result'] = generating_result.to_dict()
        input_object.add_data('generating_result', generating_result)
        # Also add as expressing_result for compatibility with ReviewingAgentTemplate
        input_object.add_data('expressing_result', generating_result)
        return generating_result.to_dict()

    def _invoke_reviewing(self, input_object: InputObject, grr_round_results: dict) -> dict:
        """Invoke reviewing agent synchronously."""
        if not self.reviewing:
            reviewing_result = OutputObject({"score": 100})
        else:
            reviewing_result = self.reviewing.run(**input_object.to_dict())
            grr_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    async def _async_invoke_reviewing(self, input_object: InputObject, grr_round_results: dict) -> dict:
        """Invoke reviewing agent asynchronously."""
        if not self.reviewing:
            reviewing_result = OutputObject({"score": 100})
        else:
            reviewing_result = await self.reviewing.async_run(**input_object.to_dict())
            grr_round_results['reviewing_result'] = reviewing_result.to_dict()
        input_object.add_data('reviewing_result', reviewing_result)
        return reviewing_result.to_dict()

    def _invoke_rewriting(self, input_object: InputObject, grr_round_results: dict) -> dict:
        """Invoke rewriting agent synchronously."""
        if not self.rewriting:
            rewriting_result = OutputObject({})
        else:
            rewriting_result = self.rewriting.run(**input_object.to_dict())
            grr_round_results['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    async def _async_invoke_rewriting(self, input_object: InputObject, grr_round_results: dict) -> dict:
        """Invoke rewriting agent asynchronously."""
        if not self.rewriting:
            rewriting_result = OutputObject({})
        else:
            rewriting_result = await self.rewriting.async_run(**input_object.to_dict())
            grr_round_results['rewriting_result'] = rewriting_result.to_dict()
        input_object.add_data('rewriting_result', rewriting_result)
        return rewriting_result.to_dict()

    def _validate_work_pattern_members(self):
        """Validate that agents are of the correct type."""
        if self.generating and not isinstance(self.generating, GeneratingAgentTemplate):
            raise ValueError(f"{self.generating} is not of expected type GeneratingAgentTemplate.")
        if self.reviewing and not isinstance(self.reviewing, ReviewingAgentTemplate):
            raise ValueError(f"{self.reviewing} is not of expected type ReviewingAgentTemplate.")
        if self.rewriting and not isinstance(self.rewriting, RewritingAgentTemplate):
            raise ValueError(f"{self.rewriting} is not of expected type RewritingAgentTemplate.")

    def set_by_agent_model(self, **kwargs):
        """Create new instance with dynamically injected agents.

        Args:
            **kwargs: Agent instances to inject (generating, reviewing, rewriting).

        Returns:
            GRRWorkPattern: New instance with injected agents.
        """
        grr_work_pattern_instance = self.__class__()
        grr_work_pattern_instance.name = self.name
        grr_work_pattern_instance.description = self.description
        for key in ['generating', 'reviewing', 'rewriting']:
            if key in kwargs:
                setattr(grr_work_pattern_instance, key, kwargs[key])
        return grr_work_pattern_instance
