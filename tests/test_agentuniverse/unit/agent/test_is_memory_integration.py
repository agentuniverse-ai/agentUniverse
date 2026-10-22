import asyncio
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.template import is_agent_template as is_agent_template_module
from agentuniverse.agent.template.implementation_agent_template import (
    ImplementationAgentTemplate,
)
from agentuniverse.agent.template.is_agent_template import ISAgentTemplate
from agentuniverse.agent.template.supervision_agent_template import (
    SupervisionAgentTemplate,
)
from agentuniverse.base.config.component_configer.configers.agent_configer import (
    AgentConfiger,
)
from agentuniverse.base.config.component_configer.configers.prompt_configer import (
    PromptConfiger,
)
from agentuniverse.base.config.configer import Configer
from agentuniverse.prompt.prompt import Prompt

_REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
_IS_APP_DIRECTORY = _REPOSITORY_ROOT / "examples/sample_apps/is_agent_app/intelligence/agentic"
_IS_AGENT_CONFIG_DIRECTORY = _IS_APP_DIRECTORY / "agent/agent_instance/is_agent_case"
_IS_PROMPT_CONFIG_DIRECTORY = _IS_APP_DIRECTORY / "prompt/is_agent_case"
_WORK_PATTERN_RESULT = {
    "result": [
        {
            "implementation_result": {"checkpoint_output": "original result"},
            "correction_result": {"checkpoint_output": "corrected result"},
        }
    ],
    "execution_context": {"corrections_made": 1},
}


class _WorkPatternStub:
    def set_by_agent_model(self, **kwargs):
        return self

    def invoke(self, input_object, work_pattern_input, **kwargs):
        return deepcopy(_WORK_PATTERN_RESULT)

    async def async_invoke(self, input_object, work_pattern_input, **kwargs):
        return deepcopy(_WORK_PATTERN_RESULT)


def _build_template() -> ISAgentTemplate:
    template = ISAgentTemplate()
    template.agent_model = AgentModel(
        info={"name": "demo_is_agent"},
        profile={"expert_framework_enabled": False},
        memory={"name": "demo_memory"},
    )
    return template


@pytest.mark.parametrize(
    ("config_name", "template_type"),
    [
        ("demo_is_agent.yaml", ISAgentTemplate),
        ("demo_implementation_agent.yaml", ImplementationAgentTemplate),
        ("demo_supervision_agent.yaml", SupervisionAgentTemplate),
    ],
)
def test_is_example_agents_configure_memory_at_top_level(config_name, template_type):
    configer = Configer(str(_IS_AGENT_CONFIG_DIRECTORY / config_name)).load()
    agent_configer = AgentConfiger(configer).load()
    template = template_type().initialize_by_component_configer(agent_configer)

    assert agent_configer.memory == {"name": "demo_memory"}
    assert "memory" not in agent_configer.profile
    assert template.memory_name == "demo_memory"
    assert template.agent_model.memory == {"name": "demo_memory"}


@pytest.mark.parametrize(
    "config_path",
    [
        "demo_implementation_agent/cn.yaml",
        "demo_supervision_agent/cn.yaml",
    ],
)
def test_is_role_prompts_consume_chat_history(config_path):
    configer = Configer(str(_IS_PROMPT_CONFIG_DIRECTORY / config_path)).load()
    prompt_configer = PromptConfiger(configer).load()
    prompt = Prompt().initialize_by_component_configer(prompt_configer)

    assert "chat_history" in prompt.input_variables


@pytest.mark.parametrize("asynchronous", [False, True])
def test_is_coordinator_uses_configured_memory_instance(asynchronous):
    template = _build_template()
    memory = MagicMock(spec=Memory)
    work_pattern = _WorkPatternStub()
    work_pattern_manager = MagicMock()
    work_pattern_manager.get_instance_obj.return_value = work_pattern
    input_object = InputObject({"input": "complete the task", "session_id": "session-1"})
    agent_input = {
        "input": "complete the task",
        "session_id": "session-1",
        "agent_id": "demo_is_agent",
    }

    with (
        patch.object(ISAgentTemplate, "process_memory", return_value=memory) as process_memory,
        patch.object(ISAgentTemplate, "_generate_agents", return_value={}),
        patch.object(
            is_agent_template_module,
            "WorkPatternManager",
            return_value=work_pattern_manager,
        ),
    ):
        if asynchronous:
            result = asyncio.run(template.async_execute(input_object, agent_input))
        else:
            result = template.execute(input_object, agent_input)

    assert result == _WORK_PATTERN_RESULT
    process_memory.assert_called_once_with(agent_input)
    work_pattern_manager.get_instance_obj.assert_called_once_with("is_work_pattern")
    memory.add.assert_called_once()
    messages = memory.add.call_args.args[0]
    assert [(message.type, message.content) for message in messages] == [
        (ChatMessageEnum.HUMAN.value, "complete the task"),
        (ChatMessageEnum.AI.value, "corrected result"),
    ]
    assert all(message.source == "demo_is_agent" for message in messages)
    assert memory.add.call_args.kwargs["session_id"] == "session-1"
    assert memory.add.call_args.kwargs["agent_id"] == "demo_is_agent"


@pytest.mark.parametrize("asynchronous", [False, True])
def test_is_coordinator_runs_without_memory(asynchronous):
    template = _build_template()
    work_pattern = _WorkPatternStub()
    work_pattern_manager = MagicMock()
    work_pattern_manager.get_instance_obj.return_value = work_pattern
    input_object = InputObject({"input": "complete the task"})
    agent_input = {"input": "complete the task"}

    with (
        patch.object(ISAgentTemplate, "process_memory", return_value=None),
        patch.object(ISAgentTemplate, "_generate_agents", return_value={}),
        patch.object(
            is_agent_template_module,
            "WorkPatternManager",
            return_value=work_pattern_manager,
        ),
    ):
        if asynchronous:
            result = asyncio.run(template.async_execute(input_object, agent_input))
        else:
            result = template.execute(input_object, agent_input)

    assert result == _WORK_PATTERN_RESULT
    work_pattern_manager.get_instance_obj.assert_called_once_with("is_work_pattern")
