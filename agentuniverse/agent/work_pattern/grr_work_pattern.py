from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.critique_agent_template import CritiqueAgentTemplate
from agentuniverse.agent.template.generate_agent_template import GenerateAgentTemplate
from agentuniverse.agent.template.rewrite_agent_template import RewriteAgentTemplate
from agentuniverse.agent.work_pattern.work_pattern import WorkPattern


class GrrWorkPattern(WorkPattern):
    generate: GenerateAgentTemplate = None
    critique: CritiqueAgentTemplate = None
    rewrite: RewriteAgentTemplate = None

    def invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        print("test grr work flow")

    async def async_invoke(self, input_object: InputObject, work_pattern_input: dict, **kwargs) -> dict:
        pass

    def set_by_agent_model(self, **kwargs):
        grr_work_pattern_instance = self.__class__()
        grr_work_pattern_instance.name = self.name
        grr_work_pattern_instance.description = self.description
        for key in ['generate', 'critique', 'rewrite']:
            if key in kwargs:
                setattr(grr_work_pattern_instance, key, kwargs[key])
        return grr_work_pattern_instance



