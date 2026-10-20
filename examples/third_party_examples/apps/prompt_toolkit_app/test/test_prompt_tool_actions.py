# ruff: noqa: S101

import pytest

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
from agentuniverse.base.config.configer import Configer

TOOL_PACKAGE = "examples.third_party_examples.apps.prompt_toolkit_app." "intelligence.agentic.action.tool"
TOOL_INPUT_KEYS = {
    "prompt_generation_action": ["scenario_description"],
    "prompt_optimization_action": ["introduction", "target", "instruction"],
    "scenario_analysis_action": ["scenario_description"],
}
TOOL_SCHEMA_ENUMS = {
    "prompt_generation_action": (
        "complexity",
        ["simple", "medium", "complex"],
    ),
    "prompt_optimization_action": (
        "strategies",
        ["clarity", "structure", "specificity", "efficiency", "comprehensiveness"],
    ),
}


def _build_app_configer():
    configer = Configer()
    configer.value = {
        "BASE_INFO": {"appname": "prompt_toolkit_test"},
        "CORE_PACKAGE": {"default": []},
        "PLUGINS": {"llm_plugins": []},
    }
    app_configer = AppConfiger().load_by_configer(configer)
    app_configer.agent_tool_set.update(TOOL_INPUT_KEYS)
    return app_configer


@pytest.fixture
def registered_prompt_tools():
    application_config_manager = ApplicationConfigManager()
    previous_app_configer = application_config_manager._ApplicationConfigManager__app_configer
    tool_manager = ToolManager()
    previous_tool_map = tool_manager._instance_obj_map
    tool_manager._instance_obj_map = {}
    application_config_manager.app_configer = _build_app_configer()

    try:
        agent_universe = AgentUniverse()
        component_configers = agent_universe.scan(
            [TOOL_PACKAGE],
            ConfigTypeEnum.YAML,
            ComponentEnum.TOOL,
        )
        agent_universe._AgentUniverse__register(
            ComponentEnum.TOOL,
            component_configers,
        )
        yield tool_manager, component_configers
    finally:
        tool_manager._instance_obj_map = previous_tool_map
        application_config_manager._ApplicationConfigManager__app_configer = previous_app_configer


def test_tool_configs_register_concrete_actions(registered_prompt_tools):
    tool_manager, component_configers = registered_prompt_tools

    assert {configer.name for configer in component_configers} == set(TOOL_INPUT_KEYS)
    for tool_name, input_keys in TOOL_INPUT_KEYS.items():
        tool = tool_manager.get_instance_obj(tool_name)
        assert tool is not None
        assert tool.name == tool_name
        assert tool.input_keys == input_keys
        assert tool.args_model
        assert set(tool.args_model_schema["properties"]) == set(tool.args_model)
        assert tool.args_model_schema["required"] == input_keys
        assert tool.args_model_schema["additionalProperties"] is False
        assert type(tool).run is Tool.run

    for tool_name, (property_name, expected_values) in TOOL_SCHEMA_ENUMS.items():
        property_schema = tool_manager.get_instance_obj(tool_name).args_model_schema["properties"][property_name]
        if property_schema["type"] == "array":
            property_schema = property_schema["items"]
        assert property_schema["enum"] == expected_values


def test_registered_prompt_tools_execute_offline(registered_prompt_tools):
    tool_manager, _ = registered_prompt_tools

    generation_result = tool_manager.get_instance_obj("prompt_generation_action").run(
        scenario_description="为初学者生成 Python 教学助手",
        complexity=" MEDIUM ",
        constraints=["使用中文", "包含代码示例"],
    )
    assert generation_result["success"] is True
    assert generation_result["generated_prompt"]["instruction"]
    assert generation_result["metadata"]["complexity"] == "medium"

    optimization_result = tool_manager.get_instance_obj("prompt_optimization_action").run(
        introduction="你是一个助手",
        target="帮助用户",
        instruction="回答问题",
        strategies=["clarity", "structure"],
    )
    assert optimization_result["success"] is True
    assert optimization_result["optimization_result"]["strategies_used"] == [
        "clarity",
        "structure",
    ]

    analysis_result = tool_manager.get_instance_obj("scenario_analysis_action").run(
        scenario_description="为初学者生成 Python 教学助手",
        domain="技术",
        target_audience="初学者",
    )
    assert analysis_result["success"] is True
    assert analysis_result["analysis_result"]["recommended_scenario"]
    assert analysis_result["extracted_context"]["domain"]
