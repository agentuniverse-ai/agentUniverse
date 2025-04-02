from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.agent.template.critique_agent_template import CritiqueAgentTemplate
from agentuniverse.agent.template.generate_agent_template import GenerateAgentTemplate
from agentuniverse.agent.template.rewrite_agent_template import RewriteAgentTemplate
from agentuniverse.agent.work_pattern.grr_work_pattern import GrrWorkPattern
from agentuniverse.agent.work_pattern.work_pattern_manager import WorkPatternManager
from agentuniverse.base.config.component_configer.configers.agent_configer import AgentConfiger


class GrrAgentTemplate(AgentTemplate):
    generate_agent_name: str = "GenerateAgent"
    critique_agent_name: str = "CritiqueAgent"
    rewrite_agent_name: str = "RewriteAgent"
    max_critique_count: int = 3

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    # TODO 应该是从配置里读取文件来更新这里的配置
    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input.update({
            'max_critique_count': GrrAgentTemplate.max_critique_count
        })
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        pass

    def execute(self, input_object: InputObject, agent_input: dict, **kwargs) -> dict:
        memory: Memory = self.process_memory(agent_input, **kwargs)
        agents = self._generate_agents()
        grr_work_pattern: GrrWorkPattern = WorkPatternManager().get_instance_obj('grr_work_pattern')
        grr_work_pattern = grr_work_pattern.set_by_agent_model(**agents)
        work_pattern_result = self.customized_execute(input_object=input_object, agent_input=agent_input, memory=memory,
                                                      peer_work_pattern=grr_work_pattern)
        self.add_peer_memory(memory, agent_input, work_pattern_result)
        return work_pattern_result

    def _generate_agents(self) -> dict:
        generate_agent = self._get_and_validate_agent(GrrAgentTemplate.generate_agent_name, GenerateAgentTemplate)
        critique_agent = self._get_and_validate_agent(GrrAgentTemplate.critique_agent_name, CritiqueAgentTemplate)
        rewrite_agent = self._get_and_validate_agent(GrrAgentTemplate.rewrite_agent_name, RewriteAgentTemplate)
        return {'generate': generate_agent,
                'critique': critique_agent,
                'rewrite': rewrite_agent}

    def customized_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                           grr_work_pattern: GrrWorkPattern, **kwargs) -> dict:
        work_pattern_result = grr_work_pattern.invoke(input_object, agent_input)
        return work_pattern_result

    async def customized_async_execute(self, input_object: InputObject, agent_input: dict, memory: Memory,
                                       grr_work_pattern: GrrWorkPattern, **kwargs) -> dict:
        work_pattern_result = await grr_work_pattern.async_invoke(input_object, agent_input)
        return work_pattern_result

    @staticmethod
    def _get_and_validate_agent(agent_name: str, expected_type: type):
        agent = AgentManager().get_instance_obj(agent_name)
        if not agent:
            return None
        if not isinstance(agent, expected_type):
            raise ValueError(f"{agent_name} is not of the expected type {expected_type.__name__}")
        return agent

    def initialize_by_component_configer(self, component_configer: AgentConfiger) -> 'GrrAgentTemplate':
        super().initialize_by_component_configer(component_configer)

        profile = self.agent_model.profile
        plan = self.agent_model.plan.get('planner', {})
        self.generate_agent_name = profile.get('generate', plan.get('generate', GrrAgentTemplate.generate_agent_name))
        self.critique_agent_name = profile.get('critique', plan.get('critique', GrrAgentTemplate.critique_agent_name))
        self.rewrite_agent_name = profile.get('rewrite', plan.get('rewrite', GrrAgentTemplate.rewrite_agent_name))
        self.max_critique_count = profile.get('max_critique_count', GrrAgentTemplate.max_critique_count)
        self.memory_name = profile.get('memory', {}).get('name')

        return self

