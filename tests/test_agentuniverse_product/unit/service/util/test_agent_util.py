import sys
import types

import pytest

from agentuniverse.agent.agent_model import AgentModel


if "ruamel.yaml" not in sys.modules:
    ruamel_module = types.ModuleType("ruamel")
    yaml_module = types.ModuleType("ruamel.yaml")
    yaml_module.YAML = object
    ruamel_module.yaml = yaml_module
    sys.modules["ruamel"] = ruamel_module
    sys.modules["ruamel.yaml"] = yaml_module

from agentuniverse_product.service.util import agent_util


class MissingInstanceManager:
    def get_instance_obj(self, *_args, **_kwargs):
        return None


class RecordingLogger:
    def __init__(self):
        self.warnings = []

    def warn(self, message):
        self.warnings.append(message)


def test_get_tool_dto_list_skips_unresolved_tool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_util, "ProductManager", MissingInstanceManager)
    monkeypatch.setattr(agent_util, "ToolManager", MissingInstanceManager)
    agent_model = AgentModel(action={"tool": ["missing_tool"]})

    assert agent_util.get_tool_dto_list(agent_model) == []


@pytest.mark.parametrize(
    "expected_exception",
    [KeyError("missing"), TypeError("invalid type"), ValueError("invalid value")],
)
def test_assemble_peer_planner_members_returns_empty_list_and_logs_expected_errors(
    monkeypatch, expected_exception
):
    logger = RecordingLogger()
    monkeypatch.setattr(agent_util, "LOGGER", logger)

    def raise_expected_error(planner, keys):
        raise expected_exception

    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", raise_expected_error)

    result = agent_util.assemble_peer_planner_members({}, object())

    assert result == []
    assert len(logger.warnings) == 1
    assert "falling back to []" in logger.warnings[0]
    assert str(expected_exception) in logger.warnings[0]


def test_assemble_peer_planner_members_propagates_unexpected_attribute_error(monkeypatch):
    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", lambda planner, keys: True)

    class BrokenAgentModel:
        @property
        def profile(self):
            raise AttributeError

    with pytest.raises(AttributeError):
        agent_util.assemble_peer_planner_members({}, BrokenAgentModel())


def test_assemble_peer_planner_members_assembles_normal_configuration(monkeypatch):
    planner = {
        "planning": "planning-agent",
        "executing": "executing-agent",
        "expressing": "expressing-agent",
        "reviewing": "reviewing-agent",
    }
    assembled = object()
    calls = []

    monkeypatch.setattr(agent_util, "dict_does_not_contain_keys", lambda planner, keys: False)

    def assemble(planner_data, member_keys):
        calls.append((planner_data, member_keys))
        return assembled

    monkeypatch.setattr(agent_util, "assemble_planner_members", assemble)

    result = agent_util.assemble_peer_planner_members(planner, object())

    assert result is assembled
    assert calls == [(planner, ["planning", "executing", "expressing", "reviewing"])]
