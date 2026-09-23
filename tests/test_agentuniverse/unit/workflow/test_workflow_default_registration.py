"""Workflow configuration should preserve base component registration metadata."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.configers.workflow_configer import WorkflowConfiger


def test_configured_default_workflow_registers_as_default():
    # Avoid importing optional integrations from the graph's node registry.
    graph_module = ModuleType("agentuniverse.workflow.graph.graph")
    graph_module.Graph = type("Graph", (), {})
    workflow_path = Path(__file__).parents[4] / "agentuniverse/workflow/workflow.py"
    spec = importlib.util.spec_from_file_location("_workflow_default_test", workflow_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"agentuniverse.workflow.graph.graph": graph_module}):
        spec.loader.exec_module(module)

    workflow = module.Workflow()
    raw_config = Configer()
    raw_config.value = {"id": "default-workflow", "name": "default-workflow",
                        "graph": {"nodes": []}, "default_symbol": True}
    config = WorkflowConfiger(raw_config).load()
    workflow.initialize_by_component_configer(config)
    manager = ComponentManagerBase(ComponentEnum.WORKFLOW)
    manager.register("test.workflow.default-workflow", workflow)

    assert workflow.default_symbol is True
    assert manager.get_default_instance() is workflow
