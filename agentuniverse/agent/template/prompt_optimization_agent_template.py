from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.prompt_exec_agent_template import PromptExecAgentTemplate
from agentuniverse.agent.template.prompt_feedback_agent_template import PromptFeedbackAgentTemplate
from agentuniverse.agent.template.prompt_scoring_agent_template import PromptScoringAgentTemplate
from agentuniverse.agent.work_pattern.prompt_optimization_work_pattern import PromptOptimizationWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.agent.agent_manager import AgentManager


class PromptOptimizationAgentTemplate(AgentTemplate):
    executing_agent_name: str = "PromptExecAgent"
    scoring_agent_name: str = "PromptScoringAgent"
    feedback_agent_name: str = "PromptFeedbackAgent"

    batch_size: int = 3
    max_iterations: int = 5
    avg_score_threshold: Optional[float] = None
    pass_rate_threshold: Optional[float] = None
    pass_score: float = 60
    initial_prompt: Optional[str] = None
    samples: Optional[list[str]] = None

    def input_keys(self) -> list[str]:
        return ['samples']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:

        agent_input['samples'] = input_object.get_data('samples') or self.samples or []
        agent_input['batch_size'] = input_object.get_data('batch_size') or self.batch_size
        agent_input['max_iterations'] = input_object.get_data('max_iterations') or self.max_iterations
        agent_input['avg_score_threshold'] = input_object.get_data('avg_score_threshold') or self.avg_score_threshold
        agent_input['pass_rate_threshold'] = input_object.get_data('pass_rate_threshold') or self.pass_rate_threshold
        agent_input['pass_score'] = input_object.get_data('pass_score') or self.pass_score
        agent_input['initial_prompt'] = input_object.get_data('initial_prompt') or self.initial_prompt or ''
        agent_input['scoring_standard'] = input_object.get_data('scoring_standard',"")
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result.get('result')}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        pattern: PromptOptimizationWorkPattern = WorkPatternManager().get_instance_obj('prompt_optimization_work_pattern')
        pattern = pattern.set_by_agent_model(**agents)
        result = pattern.invoke(input_object=input_object, work_pattern_input=agent_input)
        self.add_memory(memory, agent_input, agent_input=agent_input)
        return result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        pattern: PromptOptimizationWorkPattern = WorkPatternManager().get_instance_obj('prompt_optimization_work_pattern')
        pattern = pattern.set_by_agent_model(**agents)
        result = await pattern.async_invoke(input_object=input_object, work_pattern_input=agent_input)
        self.add_memory(memory, agent_input, agent_input=agent_input)
        return result

    def _get_and_validate_agent(self, agent_name: str, expected_type: type) -> AgentTemplate:
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        # if not isinstance(agent, expected_type):
        #     raise TypeError(f"Agent '{agent_name}' is not of type {expected_type.__name__}.")
        return agent

    def _generate_agents(self) -> dict:
        profile = self.agent_model.profile or {}
        executing_agent_name = profile.get('executing_agent_name', self.executing_agent_name)
        scoring_agent_name = profile.get('scoring_agent_name', self.scoring_agent_name)
        feedback_agent_name = profile.get('feedback_agent_name', self.feedback_agent_name)
        
        executing_agent = self._get_and_validate_agent(executing_agent_name, PromptExecAgentTemplate)
        scoring_agent = self._get_and_validate_agent(scoring_agent_name, PromptScoringAgentTemplate)
        feedback_agent = self._get_and_validate_agent(feedback_agent_name, PromptFeedbackAgentTemplate)
        return {'executing': executing_agent, 'scoring': scoring_agent, 'feedback': feedback_agent}
