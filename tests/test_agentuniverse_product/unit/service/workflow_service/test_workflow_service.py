import sys
import types
from types import SimpleNamespace


if "ruamel.yaml" not in sys.modules:
    ruamel_module = types.ModuleType("ruamel")
    yaml_module = types.ModuleType("ruamel.yaml")
    yaml_module.YAML = object
    ruamel_module.yaml = yaml_module
    sys.modules["ruamel"] = ruamel_module
    sys.modules["ruamel.yaml"] = yaml_module

from agentuniverse_product.service.model.workflow_dto import WorkflowDTO
from agentuniverse_product.service.workflow_service import workflow_service


class WorkflowManagerStub:
    def __init__(self, workflow):
        self.workflow = workflow

    def get_instance_obj(self, **_kwargs):
        return self.workflow


def test_update_workflow_preserves_omitted_fields(monkeypatch):
    workflow = SimpleNamespace(
        id="workflow-1",
        name="old name",
        description="old description",
        graph_config={"nodes": ["keep"]},
        component_config_path="workflow.yaml",
    )
    persisted_updates = []
    monkeypatch.setattr(
        workflow_service,
        "WorkflowManager",
        lambda: WorkflowManagerStub(workflow),
    )
    monkeypatch.setattr(
        workflow_service,
        "update_nested_yaml_value",
        lambda _path, updates: persisted_updates.append(updates.copy()),
    )

    result = workflow_service.WorkflowService.update_workflow(
        WorkflowDTO(id="workflow-1", name="new name")
    )

    assert result == "workflow-1"
    assert workflow.name == "new name"
    assert workflow.description == "old description"
    assert workflow.graph_config == {"nodes": ["keep"]}
    assert persisted_updates == [{"name": "new name"}]
