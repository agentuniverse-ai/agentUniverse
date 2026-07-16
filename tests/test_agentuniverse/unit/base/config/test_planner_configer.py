from agentuniverse.base.config.component_configer.configers.planner_configer import (
    PlannerConfiger,
)
from agentuniverse.base.config.configer import Configer


def test_load_by_configer_preserves_planner_keys():
    configer = Configer()
    configer.value = {
        "name": "custom_planner",
        "description": "planner with custom data keys",
        "input_key": "question",
        "output_key": "answer",
        "memory_key": "history",
    }

    planner_configer = PlannerConfiger().load_by_configer(configer)

    assert planner_configer.input_key == "question"
    assert planner_configer.output_key == "answer"
    assert planner_configer.memory_key == "history"
