from typing import Optional

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.answer_agent_template import AnswerAgentTemplate
from agentuniverse.agent.template.feedback_agent_template import FeedbackAgentTemplate
from agentuniverse.agent.template.scoring_agent_template import ScoringAgentTemplate
from agentuniverse.agent.work_pattern.optimization_work_pattern import OptimizationWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.agent.agent_manager import AgentManager


class OptimizationAgentTemplate(AgentTemplate):
    executing_agent_name: str = "AnswerAgent"
    scoring_agent_name: str = "ScoringAgent"
    feedback_agent_name: str = "FeedbackAgent"

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
        agent_input['max_history_records'] = input_object.get_data('max_history_records',"5")
        agent_input['max_feedback_chars'] = input_object.get_data('max_feedback_chars',"10000")
        
        # 处理initial_prompt逻辑：支持直接传入initial_prompt或agent_name
        initial_prompt = input_object.get_data('initial_prompt') or self.initial_prompt
        agent_name_for_optimization = input_object.get_data('agent_name_for_optimization','')
        
        if agent_name_for_optimization:
            # 如果传入了agent_name_for_optimization，从指定agent获取instruction作为initial_prompt
            try:
                source_agent = self._get_and_validate_agent(agent_name_for_optimization, AgentTemplate)
                if source_agent and source_agent.agent_model and source_agent.agent_model.profile:
                    instruction = source_agent.agent_model.profile.get('instruction', '')
                    if instruction:
                        initial_prompt = instruction
                        agent_input['agent_name_for_optimization']=agent_name_for_optimization
                        # 设置executing_agent_name为agent_name_for_optimization，这样后续调用executing_agent时就可以使用用户传入的agent
                        self.executing_agent_name = agent_name_for_optimization
                        # 设置标志位，表示这是通过agent_name_for_optimization设置的，优先级高于profile配置
                        self._agent_name_for_optimization_flag = True
                    else:
                        print(f"Warning: Agent '{agent_name_for_optimization}' does not have an instruction in its profile.")
                else:
                    print(f"Warning: Could not retrieve profile from agent '{agent_name_for_optimization}'.")
            except Exception as e:
                print(f"Warning: Failed to get instruction from agent '{agent_name_for_optimization}': {str(e)}")
                # 如果获取失败，回退到原有的initial_prompt或空字符串
                initial_prompt = initial_prompt or ''
        else:
            # 如果没有传入agent_name，使用原有的initial_prompt逻辑
            initial_prompt = initial_prompt or ''
            
        agent_input['initial_prompt'] = initial_prompt
        agent_input['scoring_standard'] = input_object.get_data('scoring_standard',"")
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result.get('result')}

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        pattern: OptimizationWorkPattern = WorkPatternManager().get_instance_obj('optimization_work_pattern')
        pattern = pattern.set_by_agent_model(**agents)
        result = pattern.invoke(input_object=input_object, work_pattern_input=agent_input)
        self.add_memory(memory, agent_input, agent_input=agent_input)
        return result

    async def async_execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        pattern: OptimizationWorkPattern = WorkPatternManager().get_instance_obj('optimization_work_pattern')
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
        
        # 优先级：运行时设置的agent_name > profile配置 > 默认值
        # 检查是否通过agent_name_for_optimization设置了新的executing_agent_name
        if hasattr(self, '_agent_name_for_optimization_flag') and self._agent_name_for_optimization_flag:
            # 使用运行时设置的agent名称
            executing_agent_name = self.executing_agent_name
            # 重置标志，避免影响后续调用
            self._agent_name_for_optimization_flag = False
        else:
            # 使用profile配置或默认值
            executing_agent_name = profile.get('executing_agent_name', self.executing_agent_name)
            
        scoring_agent_name = profile.get('scoring_agent_name', self.scoring_agent_name)
        feedback_agent_name = profile.get('feedback_agent_name', self.feedback_agent_name)
        
        executing_agent = self._get_and_validate_agent(executing_agent_name, AnswerAgentTemplate)
        scoring_agent = self._get_and_validate_agent(scoring_agent_name, ScoringAgentTemplate)
        feedback_agent = self._get_and_validate_agent(feedback_agent_name, FeedbackAgentTemplate)
        return {'executing': executing_agent, 'scoring': scoring_agent, 'feedback': feedback_agent}
