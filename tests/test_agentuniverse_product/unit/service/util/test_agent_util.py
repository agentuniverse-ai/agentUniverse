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


def test_get_tool_dto_list_skips_unresolved_tool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_util, "ProductManager", MissingInstanceManager)
    monkeypatch.setattr(agent_util, "ToolManager", MissingInstanceManager)
    agent_model = AgentModel(action={"tool": ["missing_tool"]})

    assert agent_util.get_tool_dto_list(agent_model) == []
