import pytest

from agentuniverse.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger
from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.config.component_configer.configers.planner_configer import PlannerConfiger
from agentuniverse.base.config.component_configer.configers.prompt_configer import PromptConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.component_configer.configers.work_pattern_configer import WorkPatternConfiger
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger
from agentuniverse.base.config.configer import Configer


@pytest.mark.parametrize(
    ("configer_class", "value"),
    [
        (KnowledgeConfiger, {"name": "knowledge"}),
        (LLMConfiger, {"name": "llm"}),
        (MemoryConfiger, {"name": "memory"}),
        (PlannerConfiger, {"name": "planner"}),
        (PromptConfiger, {"metadata": {"version": "1.0"}}),
        (ToolConfiger, {"name": "tool"}),
        (WorkflowConfiger, {"name": "workflow"}),
        (WorkPatternConfiger, {"name": "work_pattern"}),
    ],
)
def test_load_uses_configer_passed_to_constructor(configer_class, value):
    configer = Configer()
    configer.value = value

    loaded = configer_class(configer).load()

    assert loaded.configer is configer
