import subprocess
import sys
from pathlib import Path

import pytest

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse_product.service.util import agent_util


class MissingInstanceManager:
    def get_instance_obj(self, *_args, **_kwargs):
        return None


def test_collection_preserves_yaml_serialization():
    """Collecting this module must not replace the YAML implementation."""
    result = subprocess.run(
        [sys.executable, "-c", """
import importlib
from io import StringIO

importlib.import_module(
    "tests.test_agentuniverse_product.unit.service.util.test_agent_util"
)
from agentuniverse_product.base.util.yaml_util import YAML

yaml = YAML()
stream = StringIO()
yaml.dump({"name": "workflow"}, stream)
assert yaml.load(stream.getvalue()) == {"name": "workflow"}
"""],
        cwd=Path(__file__).resolve().parents[5],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_get_tool_dto_list_skips_unresolved_tool(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(agent_util, "ProductManager", MissingInstanceManager)
    monkeypatch.setattr(agent_util, "ToolManager", MissingInstanceManager)
    agent_model = AgentModel(action={"tool": ["missing_tool"]})

    assert agent_util.get_tool_dto_list(agent_model) == []
